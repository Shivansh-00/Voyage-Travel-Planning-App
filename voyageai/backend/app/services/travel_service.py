import hashlib
from app.schemas.travel import TravelRequest, TravelResponse
from app.schemas.state import TravelGraphState
from app.services.travel_graph import TravelGraphService
from app.memory.cache import RedisCache


class TravelService:
    def __init__(self, cache: RedisCache):
        self.cache = cache
        self.graph = TravelGraphService().build()

    async def plan(self, request: TravelRequest) -> TravelResponse:
        cache_key = 'trip:' + hashlib.sha256(request.model_dump_json().encode()).hexdigest()
        cached = await self.cache.get_json(cache_key)
        if cached:
            return TravelResponse.model_validate(cached)

        initial_state: TravelGraphState = {
            'request': request,
            'flight_options': [],
            'hotel_options': [],
            'experiences': [],
            'itinerary': [],
            'total_cost': 0.0,
            'risk_score': 0.0,
            'optimization_summary': '',
            'logs': [],
            'memory_context': '',
        }
        result = await self.graph.ainvoke(initial_state)
        response = TravelResponse(
            itinerary=result['itinerary'],
            total_cost=result['total_cost'],
            risk_score=result['risk_score'],
            optimization_summary=result['optimization_summary'],
        )
        await self.cache.set_json(cache_key, response.model_dump())
        return response
