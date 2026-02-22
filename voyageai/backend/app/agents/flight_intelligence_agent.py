"""
Agent — Flight Intelligence

Searches mock flight data for every leg implied by the route and picks
the best-value option for each.
"""

from __future__ import annotations

from app.agents.base import BaseAgent
from app.schemas.state import TravelGraphState
from app.tools.mock_apis import search_flights


class FlightIntelligenceAgent(BaseAgent):
    name = 'FlightIntelligenceAgent'

    async def run(self, state: TravelGraphState) -> TravelGraphState:
        intent = state['intent']
        origin = intent.origin_city or 'Delhi'
        destinations = intent.destinations or ['Unknown']

        all_options: list[dict] = []
        total_flight_cost = 0.0

        # outbound legs
        prev = origin
        for dest in destinations:
            flights = await search_flights(prev, dest)
            all_options.extend(flights)
            cheapest = min(flights, key=lambda f: f['price_inr'])
            total_flight_cost += cheapest['price_inr']
            prev = dest

        # return leg
        flights = await search_flights(destinations[-1], origin)
        all_options.extend(flights)
        cheapest = min(flights, key=lambda f: f['price_inr'])
        total_flight_cost += cheapest['price_inr']

        state['flight_options'] = all_options
        state['cost_breakdown'].flights_estimated = total_flight_cost

        self.log(
            state,
            f'Evaluated {len(all_options)} flight options across '
            f'{len(destinations)+1} legs. Total flight cost: ₹{total_flight_cost:,.0f}.'
        )
        return state
