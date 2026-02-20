export type ItineraryItem = {
  day: number
  activity: string
  location: string
  estimated_cost: number
  category: 'flight' | 'hotel' | 'experience' | 'transport' | 'misc'
}

export type TravelResponse = {
  itinerary: ItineraryItem[]
  total_cost: number
  risk_score: number
  optimization_summary: string
}
