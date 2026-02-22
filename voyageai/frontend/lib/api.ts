import { TravelResponse } from '@/types/travel'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? '/api/v1/plan'

export async function fetchPlan(prompt: string): Promise<TravelResponse> {
  const payload = { prompt }

  let res: Response
  try {
    res = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
  } catch (err) {
    throw new Error(
      'Network error — is the backend running on port 8000? ' +
      (err instanceof Error ? err.message : String(err))
    )
  }

  if (!res.ok) {
    const body = await res.text().catch(() => '')
    throw new Error(
      `Backend returned ${res.status}: ${body.slice(0, 200) || res.statusText}`
    )
  }
  return (await res.json()) as TravelResponse
}
