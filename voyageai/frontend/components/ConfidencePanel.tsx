'use client'
import { motion } from 'framer-motion'
import { ConfidenceScores } from '@/types/travel'

const SCORE_META: { key: keyof Omit<ConfidenceScores, 'overall'>; label: string; icon: string }[] = [
  { key: 'intent_parsing', label: 'Intent', icon: '🧠' },
  { key: 'route_planning', label: 'Route', icon: '🗺️' },
  { key: 'flight_data', label: 'Flights', icon: '✈️' },
  { key: 'hotel_data', label: 'Hotels', icon: '🏨' },
  { key: 'activity_data', label: 'Activities', icon: '🎭' },
  { key: 'budget_optimization', label: 'Budget', icon: '💰' },
  { key: 'risk_assessment', label: 'Risk', icon: '⚡' },
]

function scoreColor(score: number): string {
  if (score >= 0.8) return 'text-emerald-400'
  if (score >= 0.6) return 'text-amber-400'
  return 'text-red-400'
}

function barColor(score: number): string {
  if (score >= 0.8) return 'bg-emerald-400'
  if (score >= 0.6) return 'bg-amber-400'
  return 'bg-red-400'
}

export function ConfidencePanel({ scores }: { scores: ConfidenceScores }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="glass-card p-5"
    >
      <div className="mb-4 flex items-center justify-between">
        <h3 className="section-label">AI Confidence</h3>
        <div className="flex items-center gap-2">
          <span className={`text-2xl font-bold ${scoreColor(scores.overall)}`}>
            {Math.round(scores.overall * 100)}%
          </span>
        </div>
      </div>

      <div className="space-y-2.5">
        {SCORE_META.map(({ key, label, icon }) => {
          const value = scores[key]
          return (
            <div key={key} className="flex items-center gap-3">
              <span className="w-5 text-center text-sm">{icon}</span>
              <span className="w-20 text-xs text-slate-400">{label}</span>
              <div className="flex-1">
                <div className="h-1.5 rounded-full bg-surface-2/60 overflow-hidden">
                  <motion.div
                    className={`h-full rounded-full ${barColor(value)}`}
                    initial={{ width: 0 }}
                    animate={{ width: `${value * 100}%` }}
                    transition={{ duration: 0.8, delay: 0.1 }}
                  />
                </div>
              </div>
              <span className={`w-10 text-right text-xs font-medium ${scoreColor(value)}`}>
                {Math.round(value * 100)}%
              </span>
            </div>
          )
        })}
      </div>
    </motion.div>
  )
}
