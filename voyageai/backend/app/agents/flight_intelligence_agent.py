from app.agents.base import BaseAgent
from app.schemas.state import TravelGraphState
from app.tools.mock_apis import search_flights


class FlightIntelligenceAgent(BaseAgent):
    name = 'FlightIntelligenceAgent'

    async def run(self, state: TravelGraphState) -> TravelGraphState:
        req = state['request']
        flights = await search_flights(req.origin, req.destination)
        state['flight_options'] = flights
        cheapest = min(flights, key=lambda f: f['price'])
        state['itinerary'][0].estimated_cost = cheapest['price']
        self.log(state, f"Ranked {len(flights)} flight options. Selected {cheapest['carrier']}.")
        return state
