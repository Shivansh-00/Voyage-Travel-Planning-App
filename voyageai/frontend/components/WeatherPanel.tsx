'use client'
import { motion } from 'framer-motion'
import { WeatherInsight } from '@/types/travel'

function weatherIcon(temp: number, rain: number): string {
  if (rain > 0.4) return '🌧️'
  if (temp > 35) return '🔥'
  if (temp > 28) return '☀️'
  if (temp > 15) return '🌤️'
  if (temp > 5) return '🌥️'
  return '❄️'
}

export function WeatherPanel({ insights }: { insights: WeatherInsight[] }) {
  if (!insights.length) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
      className="glass-card p-5"
    >
      <h3 className="section-label mb-4">Weather Intelligence</h3>

      <div className="grid gap-3 sm:grid-cols-2">
        {insights.map((wi, i) => (
          <motion.div
            key={wi.city}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 * i }}
            className="rounded-xl bg-surface-2/30 p-4"
          >
            <div className="mb-2 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-xl">{weatherIcon(wi.avg_temp_c, wi.rain_chance)}</span>
                <span className="text-sm font-semibold text-slate-200">{wi.city}</span>
              </div>
              <span className="text-lg font-bold text-slate-300">{wi.avg_temp_c}°C</span>
            </div>

            <div className="mb-2 flex gap-3 text-xs text-slate-400">
              <span>🌧 {Math.round(wi.rain_chance * 100)}% rain</span>
              <span
                className={
                  wi.advisory === 'low'
                    ? 'text-emerald-400'
                    : wi.advisory === 'moderate'
                    ? 'text-amber-400'
                    : 'text-red-400'
                }
              >
                {wi.advisory} risk
              </span>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">{wi.recommendation}</p>

            {wi.best_months.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {wi.best_months.slice(0, 4).map((m) => (
                  <span
                    key={m}
                    className="rounded-full bg-surface-2/60 px-2 py-0.5 text-[10px] text-slate-500"
                  >
                    {m}
                  </span>
                ))}
              </div>
            )}
          </motion.div>
        ))}
      </div>
    </motion.div>
  )
}
