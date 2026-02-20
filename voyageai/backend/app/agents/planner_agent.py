from app.agents.base import BaseAgent
from app.schemas.travel import ItineraryItem
from app.schemas.state import TravelGraphState


class PlannerAgent(BaseAgent):
    name = 'PlannerAgent'

    async def run(self, state: TravelGraphState) -> TravelGraphState:
        req = state['request']
        itinerary = [
            ItineraryItem(day=1, activity=f'Flight from {req.origin} to {req.destination}', location=req.destination, estimated_cost=0, category='flight'),
            ItineraryItem(day=2, activity='City orientation and local transit pass', location=req.destination, estimated_cost=25, category='transport'),
        ]
        state['itinerary'] = itinerary
        self.log(state, 'Generated base itinerary skeleton.')
        return state
