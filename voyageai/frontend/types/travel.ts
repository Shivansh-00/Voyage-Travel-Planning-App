// ---------------------------------------------------------------------------
// User Intent (extracted from natural language)
// ---------------------------------------------------------------------------

export type BudgetRange = {
  min: number | null
  max: number | null
}

export type UserIntent = {
  origin_city: string | null
  destinations: string[]
  country: string | null
  duration_days: number
  travel_month: string | null
  travel_year: number | null
  budget_total_inr: number | null
  budget_range_inr: BudgetRange
  trip_type: string[]
  traveler_count: number
  accommodation_preferences: string[]
  interests: string[]
  transport_preferences: string[]
  special_requirements: string[]
}

// ---------------------------------------------------------------------------
// Plan models
// ---------------------------------------------------------------------------

export type DayItinerary = {
  day: number
  city: string
  activities: string[]
  estimated_cost_inr: number
  weather_note: string
}

export type TransportPlan = {
  recommended_passes: string[]
  route_order: string[]
}

export type StayRecommendation = {
  city: string
  stay_type: string
  budget_per_night_inr: number
}

export type VisaInformation = {
  required: boolean
  details: string
}

export type CostBreakdown = {
  flights_estimated: number
  accommodation_estimated: number
  activities_estimated: number
  transport_estimated: number
  total_estimated: number
}

export type RemoteWorkSpot = {
  city: string
  recommendations: string[]
}

// ---------------------------------------------------------------------------
// Carbon Footprint
// ---------------------------------------------------------------------------

export type CarbonLeg = {
  leg: string
  mode: string
  distance_km: number
  co2_kg: number
}

export type CarbonFootprint = {
  total_co2_kg: number
  rating: string
  offset_cost_inr: number
  legs: CarbonLeg[]
  tips: string[]
}

// ---------------------------------------------------------------------------
// Confidence Scoring
// ---------------------------------------------------------------------------

export type ConfidenceScores = {
  overall: number
  intent_parsing: number
  route_planning: number
  flight_data: number
  hotel_data: number
  activity_data: number
  budget_optimization: number
  risk_assessment: number
}

// ---------------------------------------------------------------------------
// Weather Insights
// ---------------------------------------------------------------------------

export type WeatherInsight = {
  city: string
  avg_temp_c: number
  rain_chance: number
  advisory: string
  best_months: string[]
  recommendation: string
}

// ---------------------------------------------------------------------------
// Plan
// ---------------------------------------------------------------------------

export type TravelPlan = {
  summary: string
  route_strategy: string
  day_by_day_itinerary: DayItinerary[]
  transport_plan: TransportPlan
  stay_recommendations: StayRecommendation[]
  visa_information: VisaInformation
  cost_breakdown: CostBreakdown
  remote_work_friendly_spots: RemoteWorkSpot[]
  optimization_score: number
  carbon_footprint: CarbonFootprint
  weather_insights: WeatherInsight[]
}

// ---------------------------------------------------------------------------
// API Response
// ---------------------------------------------------------------------------

export type TravelResponse = {
  intent: UserIntent
  plan: TravelPlan
  risk_score: number
  confidence: ConfidenceScores
  optimization_summary: string
  agent_logs: string[]
  processing_time_ms: number
}

// Legacy compat (kept for internal use)
export type ItineraryItem = {
  day: number
  activity: string
  location: string
  estimated_cost: number
  category: 'flight' | 'hotel' | 'experience' | 'transport' | 'misc'
}
