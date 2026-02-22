'use client'
import { useState, useCallback, useRef } from 'react'
import { TravelResponse } from '@/types/travel'

interface StreamState {
  step: number
  totalSteps: number
  label: string
  progress: number
  agent: string
}

export function useTravelPlan() {
  const [data, setData] = useState<TravelResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [stream, setStream] = useState<StreamState | null>(null)
  const abortRef = useRef<AbortController | null>(null)

  const generate = useCallback(async (prompt: string) => {
    // Cancel any in-flight request
    if (abortRef.current) {
      abortRef.current.abort()
    }
    const controller = new AbortController()
    abortRef.current = controller

    setLoading(true)
    setError(null)
    setData(null)
    setStream(null)

    try {
      // Try streaming first
      const res = await fetch('/api/v1/plan/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
        signal: controller.signal,
      })

      if (!res.ok) {
        // Fallback to regular endpoint
        const fallbackRes = await fetch('/api/v1/plan', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt }),
          signal: controller.signal,
        })
        if (!fallbackRes.ok) {
          const body = await fallbackRes.text().catch(() => '')
          throw new Error(`Backend returned ${fallbackRes.status}: ${body.slice(0, 200)}`)
        }
        const result = await fallbackRes.json()
        setData(result)
        return
      }

      const reader = res.body?.getReader()
      if (!reader) {
        throw new Error('Streaming not supported')
      }

      const decoder = new TextDecoder()
      let buffer = ''

      try {
        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            if (!line.startsWith('data: ')) continue
            const payload = line.slice(6).trim()
            if (payload === '[DONE]') continue

            try {
              const event = JSON.parse(payload)
              if (event.type === 'progress') {
                setStream({
                  step: event.step,
                  totalSteps: event.total_steps,
                  label: event.label,
                  progress: event.progress,
                  agent: event.agent,
                })
              } else if (event.type === 'result') {
                setData(event.data)
              } else if (event.type === 'error') {
                throw new Error(event.message)
              }
            } catch (e) {
              if (e instanceof SyntaxError) continue
              throw e
            }
          }
        }
      } finally {
        reader.releaseLock()
      }
    } catch (err) {
      // Don't treat abort as an error
      if (err instanceof DOMException && err.name === 'AbortError') return
      const msg = err instanceof Error ? err.message : 'Unknown error'
      setError(msg)
      console.error('[useTravelPlan]', msg)
    } finally {
      setStream(null)
      setLoading(false)
      if (abortRef.current === controller) {
        abortRef.current = null
      }
    }
  }, [])

  return { data, loading, error, stream, generate }
}
