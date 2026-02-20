from typing import List, TypedDict
from app.schemas.travel import ItineraryItem, TravelRequest


class TravelGraphState(TypedDict):
    request: TravelRequest
    flight_options: list[dict]
    hotel_options: list[dict]
    experiences: list[dict]
    itinerary: List[ItineraryItem]
    total_cost: float
    risk_score: float
    optimization_summary: str
    logs: list[str]
    memory_context: str
