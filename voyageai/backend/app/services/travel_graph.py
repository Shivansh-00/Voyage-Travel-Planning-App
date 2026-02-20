from langgraph.graph import END, StateGraph
from app.agents.planner_agent import PlannerAgent
from app.agents.flight_intelligence_agent import FlightIntelligenceAgent
from app.agents.hotel_intelligence_agent import HotelIntelligenceAgent
from app.agents.experience_agent import ExperienceAgent
from app.agents.budget_optimizer_agent import BudgetOptimizerAgent
from app.agents.risk_analyzer_agent import RiskAnalyzerAgent
from app.agents.memory_agent import MemoryAgent
from app.schemas.state import TravelGraphState
from app.tools.vector_store import FaissVectorStore, PineconeVectorStore
from app.config import get_settings


class TravelGraphService:
    def __init__(self):
        settings = get_settings()
        if settings.vector_provider.lower() == 'pinecone':
            store = PineconeVectorStore(settings.pinecone_api_key, settings.pinecone_index, settings.pinecone_environment)
        else:
            store = FaissVectorStore()
        self.agents = {
            'planner': PlannerAgent(),
            'flight': FlightIntelligenceAgent(),
            'hotel': HotelIntelligenceAgent(),
            'experience': ExperienceAgent(),
            'budget': BudgetOptimizerAgent(),
            'risk': RiskAnalyzerAgent(),
            'memory': MemoryAgent(store),
        }

    def build(self):
        graph = StateGraph(TravelGraphState)
        graph.add_node('memory', self.agents['memory'].run)
        graph.add_node('planner', self.agents['planner'].run)
        graph.add_node('flight', self.agents['flight'].run)
        graph.add_node('hotel', self.agents['hotel'].run)
        graph.add_node('experience', self.agents['experience'].run)
        graph.add_node('budget', self.agents['budget'].run)
        graph.add_node('risk', self.agents['risk'].run)

        graph.set_entry_point('memory')
        graph.add_edge('memory', 'planner')
        graph.add_edge('planner', 'flight')
        graph.add_edge('flight', 'hotel')
        graph.add_edge('hotel', 'experience')
        graph.add_edge('experience', 'budget')
        graph.add_edge('budget', 'risk')
        graph.add_edge('risk', END)
        return graph.compile()
