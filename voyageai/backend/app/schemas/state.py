from __future__ import annotations

from typing import Any, List, Optional, TypedDict

from app.schemas.travel import (
    CarbonFootprint,
    ConfidenceScores,
    CostBreakdown,
    DayItinerary,
    RemoteWorkSpot,
    StayRecommendation,
    TransportPlan,
    UserIntent,
    VisaInformation,
    WeatherInsight,
)


class TravelGraphState(TypedDict):
    # --- input ---
    raw_prompt: str
    intent: UserIntent

    # --- data gathered by agents ---
    flight_options: list[dict[str, Any]]
    hotel_options: list[dict[str, Any]]
    experiences: list[dict[str, Any]]
    weather_data: dict[str, Any]
    visa_data: dict[str, Any]

    # --- plan artefacts ---
    day_by_day_itinerary: List[DayItinerary]
    transport_plan: TransportPlan
    stay_recommendations: List[StayRecommendation]
    visa_information: VisaInformation
    cost_breakdown: CostBreakdown
    remote_work_spots: List[RemoteWorkSpot]
    summary: str
    route_strategy: str

    # --- new features ---
    carbon_footprint: CarbonFootprint
    confidence_scores: ConfidenceScores
    weather_insights: List[WeatherInsight]

    # --- scores & metadata ---
    total_cost: float
    risk_score: float
    optimization_score: float
    optimization_summary: str
    logs: list[str]
    memory_context: str
    validation_errors: list[str]
