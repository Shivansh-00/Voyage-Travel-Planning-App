import { TravelResponse } from '@/types/travel'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api/v1/plan'

export async function fetchPlan(prompt: string): Promise<TravelResponse> {
  const payload = {
    origin: 'SFO',
    destination: prompt,
    start_date: '2026-06-01',
    end_date: '2026-06-05',
    budget: 2500,
    travelers: 1,
    preferences: ['culture', 'food']
  }

  const res = await fetch(API_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    cache: 'no-store'
  })
  if (!res.ok) {
    throw new Error('Failed to fetch itinerary')
  }
  return (await res.json()) as TravelResponse
}
