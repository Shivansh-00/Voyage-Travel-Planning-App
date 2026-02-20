import pytest

from app.agents.budget_optimizer_agent import BudgetOptimizerAgent
from app.agents.experience_agent import ExperienceAgent
from app.agents.flight_intelligence_agent import FlightIntelligenceAgent
from app.agents.hotel_intelligence_agent import HotelIntelligenceAgent
from app.agents.planner_agent import PlannerAgent
from app.schemas.travel import TravelRequest


@pytest.mark.asyncio
async def test_agent_chain_generates_costed_itinerary():
    state = {
        'request': TravelRequest(origin='SFO', destination='Tokyo', start_date='2026-06-01', end_date='2026-06-06', budget=3000),
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
    for agent in [PlannerAgent(), FlightIntelligenceAgent(), HotelIntelligenceAgent(), ExperienceAgent(), BudgetOptimizerAgent()]:
        state = await agent.run(state)

    assert len(state['itinerary']) >= 3
    assert state['total_cost'] > 0
    assert 'optimized under budget' in state['optimization_summary']
