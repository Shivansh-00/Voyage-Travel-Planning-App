"""
Travel Service — orchestrates the graph and maps the result to the API schema.
"""

from __future__ import annotations

import hashlib
import time
from typing import AsyncGenerator

from app.schemas.travel import (
    CarbonFootprint,
    ConfidenceScores,
    CostBreakdown,
    TransportPlan,
    TravelPlan,
    TravelPrompt,
    TravelResponse,
    UserIntent,
    VisaInformation,
)
from app.schemas.state import TravelGraphState
from app.services.travel_graph import TravelGraphService
from app.memory.cache import RedisCache

# Human-readable labels for each agent node
_AGENT_LABELS: dict[str, str] = {
    'intent_extractor': 'Parsing your trip description...',
    'memory': 'Loading travel memory...',
    'planner': 'Optimizing route & itinerary...',
    'flight': 'Searching flight options...',
    'hotel': 'Finding best accommodations...',
    'experience': 'Curating activities & experiences...',
    'budget': 'Optimizing budget allocation...',
    'carbon': 'Calculating carbon footprint...',
    'risk': 'Analyzing risks & visa requirements...',
    'confidence': 'Scoring confidence levels...',
    'validation': 'Validating final plan...',
}

_AGENT_ORDER = list(_AGENT_LABELS.keys())


class TravelService:
    def __init__(self, cache: RedisCache) -> None:
        self.cache = cache
        self._graph_svc = TravelGraphService()
        self.graph = self._graph_svc.build()

    def _build_initial_state(self, prompt: str) -> TravelGraphState:
        return {
            'raw_prompt': prompt,
            'intent': UserIntent(),
            'flight_options': [],
            'hotel_options': [],
            'experiences': [],
            'weather_data': {},
            'visa_data': {},
            'day_by_day_itinerary': [],
            'transport_plan': TransportPlan(),
            'stay_recommendations': [],
            'visa_information': VisaInformation(),
            'cost_breakdown': CostBreakdown(),
            'remote_work_spots': [],
            'summary': '',
            'route_strategy': '',
            'carbon_footprint': CarbonFootprint(),
            'confidence_scores': ConfidenceScores(),
            'weather_insights': [],
            'total_cost': 0.0,
            'risk_score': 0.0,
            'optimization_score': 0.0,
            'optimization_summary': '',
            'logs': [],
            'memory_context': '',
            'validation_errors': [],
        }

    def _build_response(self, result: dict, elapsed_ms: float) -> TravelResponse:
        return TravelResponse(
            intent=result['intent'],
            plan=TravelPlan(
                summary=result.get('summary', ''),
                route_strategy=result.get('route_strategy', ''),
                day_by_day_itinerary=result.get('day_by_day_itinerary', []),
                transport_plan=result.get('transport_plan', TransportPlan()),
                stay_recommendations=result.get('stay_recommendations', []),
                visa_information=result.get('visa_information', VisaInformation()),
                cost_breakdown=result.get('cost_breakdown', CostBreakdown()),
                remote_work_friendly_spots=result.get('remote_work_spots', []),
                optimization_score=result.get('optimization_score', 0),
                carbon_footprint=result.get('carbon_footprint', CarbonFootprint()),
                weather_insights=result.get('weather_insights', []),
            ),
            risk_score=result.get('risk_score', 0),
            confidence=result.get('confidence_scores', ConfidenceScores()),
            optimization_summary=result.get('optimization_summary', ''),
            agent_logs=result.get('logs', []),
            processing_time_ms=elapsed_ms,
        )

    async def plan(self, prompt: TravelPrompt) -> TravelResponse:
        cache_key = 'trip:' + hashlib.sha256(prompt.prompt.encode()).hexdigest()
        cached = await self.cache.get_json(cache_key)
        if cached:
            return TravelResponse.model_validate(cached)

        start_time = time.perf_counter()
        initial_state = self._build_initial_state(prompt.prompt)
        result = await self.graph.ainvoke(initial_state)
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 1)

        response = self._build_response(result, elapsed_ms)
        await self.cache.set_json(cache_key, response.model_dump())
        return response

    async def plan_stream(
        self, prompt: TravelPrompt,
    ) -> AsyncGenerator[dict, None]:
        """
        Stream agent progress events as the LangGraph executes each node.

        Yields dicts of shape:
          {"type": "progress", "agent": ..., "label": ..., "progress": ..., "step": ..., "total_steps": ...}
          {"type": "result", "data": {...}}  — final plan
          {"type": "error", "message": ...}  — on failure

        Uses LangGraph's ``astream()`` to yield after each real node
        completes, so progress events reflect actual computation.
        """
        cache_key = 'trip:' + hashlib.sha256(prompt.prompt.encode()).hexdigest()
        cached = await self.cache.get_json(cache_key)
        if cached:
            # Even for cached results, send a quick progress burst
            total = len(_AGENT_ORDER)
            for i, agent in enumerate(_AGENT_ORDER):
                yield {
                    'type': 'progress',
                    'agent': agent,
                    'label': _AGENT_LABELS.get(agent, agent),
                    'progress': round(((i + 1) / total) * 100),
                    'step': i + 1,
                    'total_steps': total,
                }
            yield {'type': 'result', 'data': cached}
            return

        start_time = time.perf_counter()
        initial_state = self._build_initial_state(prompt.prompt)
        total = len(_AGENT_ORDER)
        step = 0
        final_state: dict = {}

        try:
            async for event in self.graph.astream(initial_state):
                # astream yields {node_name: state_update} after each node
                for node_name in event:
                    final_state.update(event[node_name])
                    step += 1
                    progress = round((step / total) * 100)
                    yield {
                        'type': 'progress',
                        'agent': node_name,
                        'label': _AGENT_LABELS.get(node_name, f'Running {node_name}...'),
                        'progress': min(progress, 99),
                        'step': step,
                        'total_steps': total,
                    }

            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 1)

            # Merge final_state back with initial_state for any keys
            # that astream didn't return (they stay at initial values)
            merged = {**initial_state, **final_state}
            response = self._build_response(merged, elapsed_ms)

            yield {
                'type': 'progress',
                'agent': 'done',
                'label': 'Plan complete!',
                'progress': 100,
                'step': total,
                'total_steps': total,
            }
            result_data = response.model_dump()
            yield {'type': 'result', 'data': result_data}

            await self.cache.set_json(cache_key, result_data)

        except Exception as e:
            yield {'type': 'error', 'message': str(e)}
