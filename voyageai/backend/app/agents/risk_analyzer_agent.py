from app.agents.base import BaseAgent
from app.schemas.state import TravelGraphState
from app.tools.mock_apis import get_weather_risk


class RiskAnalyzerAgent(BaseAgent):
    name = 'RiskAnalyzerAgent'

    async def run(self, state: TravelGraphState) -> TravelGraphState:
        weather = await get_weather_risk(state['request'].destination)
        budget_ratio = state['total_cost'] / state['request'].budget if state['request'].budget else 1
        state['risk_score'] = round((weather['storm_probability'] * 0.5 + budget_ratio * 0.5) * 10, 2)
        self.log(state, f"Risk score computed at {state['risk_score']}.")
        return state
