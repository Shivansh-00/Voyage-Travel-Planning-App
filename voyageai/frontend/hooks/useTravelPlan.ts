'use client'
import { useState } from 'react'
import { fetchPlan } from '@/lib/api'
import { TravelResponse } from '@/types/travel'

export function useTravelPlan() {
  const [data, setData] = useState<TravelResponse | null>(null)
  const [loading, setLoading] = useState(false)

  const generate = async (prompt: string) => {
    setLoading(true)
    try {
      const next = await fetchPlan(prompt)
      setData(next)
    } finally {
      setLoading(false)
    }
  }

  return { data, loading, generate }
}
