from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Dict, List, Literal, Optional


# ---------------------------------------------------------------------------
# REQUEST MODELS
# ---------------------------------------------------------------------------

class TravelPrompt(BaseModel):
    """Raw natural-language trip description from the user."""
    prompt: str = Field(..., min_length=3, description="Natural language trip description")


class BudgetRange(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None


class UserIntent(BaseModel):
    """Structured fields extracted from a natural-language prompt."""
    origin_city: Optional[str] = None
    destinations: List[str] = Field(default_factory=list)
    country: Optional[str] = None
    duration_days: int = 5
    travel_month: Optional[str] = None
    travel_year: Optional[int] = None
    budget_total_inr: Optional[float] = None
    budget_range_inr: BudgetRange = Field(default_factory=BudgetRange)
    trip_type: List[str] = Field(default_factory=list)
    traveler_count: int = 1
    accommodation_preferences: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)
    transport_preferences: List[str] = Field(default_factory=list)
    special_requirements: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# PLAN OUTPUT MODELS
# ---------------------------------------------------------------------------

class DayItinerary(BaseModel):
    day: int
    city: str
    activities: List[str] = Field(default_factory=list)
    estimated_cost_inr: float = 0
    weather_note: str = ""


class TransportPlan(BaseModel):
    recommended_passes: List[str] = Field(default_factory=list)
    route_order: List[str] = Field(default_factory=list)


class StayRecommendation(BaseModel):
    city: str
    stay_type: str
    budget_per_night_inr: float


class VisaInformation(BaseModel):
    required: bool = False
    details: str = ""


class CostBreakdown(BaseModel):
    flights_estimated: float = 0
    accommodation_estimated: float = 0
    activities_estimated: float = 0
    transport_estimated: float = 0
    total_estimated: float = 0


class RemoteWorkSpot(BaseModel):
    city: str
    recommendations: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# NEW: Carbon Footprint
# ---------------------------------------------------------------------------

class CarbonLeg(BaseModel):
    """CO₂ estimate for a single travel leg."""
    leg: str = ""
    mode: str = "flight"
    distance_km: float = 0
    co2_kg: float = 0


class CarbonFootprint(BaseModel):
    """Total trip carbon footprint with per-leg breakdown."""
    total_co2_kg: float = 0
    rating: str = "moderate"           # low / moderate / high
    offset_cost_inr: float = 0
    legs: List[CarbonLeg] = Field(default_factory=list)
    tips: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# NEW: Confidence Scoring
# ---------------------------------------------------------------------------

class ConfidenceScores(BaseModel):
    """Per-agent confidence scores (0-1) plus overall."""
    overall: float = 0.0
    intent_parsing: float = 0.0
    route_planning: float = 0.0
    flight_data: float = 0.0
    hotel_data: float = 0.0
    activity_data: float = 0.0
    budget_optimization: float = 0.0
    risk_assessment: float = 0.0


# ---------------------------------------------------------------------------
# NEW: Weather Insights
# ---------------------------------------------------------------------------

class WeatherInsight(BaseModel):
    city: str
    avg_temp_c: float = 22
    rain_chance: float = 0.2
    advisory: str = "low"
    best_months: List[str] = Field(default_factory=list)
    recommendation: str = ""


# ---------------------------------------------------------------------------
# PLAN
# ---------------------------------------------------------------------------

class TravelPlan(BaseModel):
    summary: str = ""
    route_strategy: str = ""
    day_by_day_itinerary: List[DayItinerary] = Field(default_factory=list)
    transport_plan: TransportPlan = Field(default_factory=TransportPlan)
    stay_recommendations: List[StayRecommendation] = Field(default_factory=list)
    visa_information: VisaInformation = Field(default_factory=VisaInformation)
    cost_breakdown: CostBreakdown = Field(default_factory=CostBreakdown)
    remote_work_friendly_spots: List[RemoteWorkSpot] = Field(default_factory=list)
    optimization_score: float = 0
    carbon_footprint: CarbonFootprint = Field(default_factory=CarbonFootprint)
    weather_insights: List[WeatherInsight] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# API RESPONSE
# ---------------------------------------------------------------------------

class TravelResponse(BaseModel):
    intent: UserIntent
    plan: TravelPlan
    risk_score: float = 0
    confidence: ConfidenceScores = Field(default_factory=ConfidenceScores)
    optimization_summary: str = ""
    agent_logs: List[str] = Field(default_factory=list)
    processing_time_ms: float = 0


# ---------------------------------------------------------------------------
# LEGACY COMPAT (kept for internal agent use)
# ---------------------------------------------------------------------------

class ItineraryItem(BaseModel):
    day: int
    activity: str
    location: str
    estimated_cost: float
    category: Literal['flight', 'hotel', 'experience', 'transport', 'misc']


class AgentLog(BaseModel):
    agent: str
    message: str
