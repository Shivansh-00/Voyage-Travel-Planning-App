from pydantic import BaseModel, Field
from typing import List, Literal


class TravelRequest(BaseModel):
    origin: str
    destination: str
    start_date: str
    end_date: str
    budget: float = Field(gt=0)
    travelers: int = Field(default=1, ge=1)
    preferences: List[str] = Field(default_factory=list)


class ItineraryItem(BaseModel):
    day: int
    activity: str
    location: str
    estimated_cost: float
    category: Literal['flight', 'hotel', 'experience', 'transport', 'misc']


class TravelResponse(BaseModel):
    itinerary: List[ItineraryItem]
    total_cost: float
    risk_score: float
    optimization_summary: str


class AgentLog(BaseModel):
    agent: str
    message: str
