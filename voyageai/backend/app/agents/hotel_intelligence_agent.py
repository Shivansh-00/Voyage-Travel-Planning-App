from app.agents.base import BaseAgent
from app.schemas.state import TravelGraphState
from app.schemas.travel import ItineraryItem
from app.tools.mock_apis import search_hotels


class HotelIntelligenceAgent(BaseAgent):
    name = 'HotelIntelligenceAgent'

    async def run(self, state: TravelGraphState) -> TravelGraphState:
        req = state['request']
        hotels = await search_hotels(req.destination)
        state['hotel_options'] = hotels
        nights = 3
        best_value = min(hotels, key=lambda h: h['nightly_rate'])
        state['itinerary'].append(
            ItineraryItem(
                day=1,
                activity=f"Check in at {best_value['name']}",
                location=req.destination,
                estimated_cost=best_value['nightly_rate'] * nights,
                category='hotel',
            )
        )
        self.log(state, f"Selected hotel {best_value['name']} for {nights} nights.")
        return state
