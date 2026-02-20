from app.agents.base import BaseAgent
from app.schemas.state import TravelGraphState
from app.schemas.travel import ItineraryItem


class ExperienceAgent(BaseAgent):
    name = 'ExperienceAgent'

    async def run(self, state: TravelGraphState) -> TravelGraphState:
        destination = state['request'].destination
        experiences = [
            {'name': 'Cultural walking tour', 'cost': 45.0, 'score': 9.1},
            {'name': 'Food market crawl', 'cost': 55.0, 'score': 9.4},
            {'name': 'Museum pass', 'cost': 35.0, 'score': 8.2},
        ]
        state['experiences'] = experiences
        for i, exp in enumerate(experiences, start=3):
            state['itinerary'].append(
                ItineraryItem(day=i, activity=exp['name'], location=destination, estimated_cost=exp['cost'], category='experience')
            )
        self.log(state, f'Added {len(experiences)} experiences.')
        return state
