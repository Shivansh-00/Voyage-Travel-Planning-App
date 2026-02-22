"""
LangGraph multi-agent orchestration.

Pipeline:
  Intent Extraction → Memory → Planner (Route Optimizer)
  → Flight Intelligence → Hotel Intelligence → Experience Curator
  → Budget Optimizer → Carbon Footprint → Risk + Visa + Weather
  → Confidence Scoring → Validation → END
"""

from __future__ import annotations

from langgraph.graph import END, StateGraph

from app.agents.intent_extractor_agent import IntentExtractorAgent
from app.agents.planner_agent import PlannerAgent
from app.agents.flight_intelligence_agent import FlightIntelligenceAgent
from app.agents.hotel_intelligence_agent import HotelIntelligenceAgent
from app.agents.experience_agent import ExperienceAgent
from app.agents.budget_optimizer_agent import BudgetOptimizerAgent
from app.agents.risk_analyzer_agent import RiskAnalyzerAgent
from app.agents.memory_agent import MemoryAgent
from app.agents.validation_agent import ValidationAgent
from app.agents.carbon_agent import CarbonFootprintAgent
from app.agents.confidence_agent import ConfidenceAgent
from app.config import get_settings
from app.schemas.state import TravelGraphState
from app.tools.vector_store import FaissVectorStore, PineconeVectorStore


class TravelGraphService:
    def __init__(self) -> None:
        settings = get_settings()
        if settings.vector_provider.lower() == 'pinecone':
            store = PineconeVectorStore(
                settings.pinecone_api_key,
                settings.pinecone_index,
                settings.pinecone_environment,
            )
        else:
            store = FaissVectorStore()

        self.agents = {
            'intent_extractor': IntentExtractorAgent(),
            'memory': MemoryAgent(store),
            'planner': PlannerAgent(),
            'flight': FlightIntelligenceAgent(),
            'hotel': HotelIntelligenceAgent(),
            'experience': ExperienceAgent(),
            'budget': BudgetOptimizerAgent(),
            'carbon': CarbonFootprintAgent(),
            'risk': RiskAnalyzerAgent(),
            'confidence': ConfidenceAgent(),
            'validation': ValidationAgent(),
        }

    def build(self):
        graph = StateGraph(TravelGraphState)

        # ── register nodes ────────────────────────────────────────────
        for name, agent in self.agents.items():
            graph.add_node(name, agent.run)

        # ── edge flow  ─────────────────────────────────────────────
        graph.set_entry_point('intent_extractor')
        graph.add_edge('intent_extractor', 'memory')
        graph.add_edge('memory', 'planner')
        graph.add_edge('planner', 'flight')
        graph.add_edge('flight', 'hotel')
        graph.add_edge('hotel', 'experience')
        graph.add_edge('experience', 'budget')
        graph.add_edge('budget', 'carbon')
        graph.add_edge('carbon', 'risk')
        graph.add_edge('risk', 'confidence')
        graph.add_edge('confidence', 'validation')
        graph.add_edge('validation', END)

        return graph.compile()
