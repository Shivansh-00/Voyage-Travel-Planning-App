'use client'
import { FormEvent, useState } from 'react'
import { motion } from 'framer-motion'

const EXAMPLES = [
  '7-day Japan trip (Tokyo + Kyoto) from Delhi, ₹2L budget, love food & culture',
  'Solo backpacking to Bali & Bangkok, 10 days, March, 80k budget',
  'Luxury honeymoon in Maldives, 5 nights, boutique resort',
  'Family trip to Dubai & Singapore, 2 weeks, 4 people, ₹5 lakhs',
]

export function ChatPanel({
  onSubmit,
  loading,
}: {
  onSubmit: (message: string) => Promise<void>
  loading?: boolean
}) {
  const [value, setValue] = useState('')

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!value.trim() || loading) return
    await onSubmit(value)
  }

  return (
    <motion.form
      onSubmit={handleSubmit}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card p-5"
    >
      <label className="section-label mb-3 block">
        Describe your dream trip
      </label>
      <textarea
        rows={3}
        className="w-full rounded-xl bg-surface-2/50 p-4 text-sm leading-relaxed text-slate-200 placeholder-slate-600 border border-surface-3/30 focus:border-brand/40 focus:outline-none focus:ring-1 focus:ring-brand/30 transition-all resize-none"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="e.g. Solo backpacking trip to Bali and Bangkok for 10 days in March, budget 80k, love adventure and street food"
      />

      {/* Quick examples */}
      {!value && (
        <div className="mt-3 flex flex-wrap gap-1.5">
          {EXAMPLES.map((ex, i) => (
            <button
              key={i}
              type="button"
              onClick={() => setValue(ex)}
              className="rounded-lg bg-surface-2/30 px-2.5 py-1 text-[11px] text-slate-500 hover:text-brand hover:bg-brand/5 transition-colors border border-transparent hover:border-brand/20"
            >
              {ex.slice(0, 50)}…
            </button>
          ))}
        </div>
      )}

      <button
        type="submit"
        disabled={loading || !value.trim()}
        className="btn-primary mt-4 w-full px-6 py-3 text-sm text-white disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {loading ? (
          <>
            <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Planning your trip…
          </>
        ) : (
          <>✨ Generate Plan</>
        )}
      </button>
    </motion.form>
  )
}
