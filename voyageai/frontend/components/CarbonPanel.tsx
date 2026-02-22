'use client'
import { motion } from 'framer-motion'
import { CarbonFootprint } from '@/types/travel'

const RATING_CONFIG: Record<string, { color: string; bg: string; barBg: string; icon: string }> = {
  low: { color: 'text-emerald-400', bg: 'bg-emerald-400/10', barBg: 'bg-emerald-400', icon: '🌱' },
  moderate: { color: 'text-amber-400', bg: 'bg-amber-400/10', barBg: 'bg-amber-400', icon: '🌿' },
  high: { color: 'text-orange-400', bg: 'bg-orange-400/10', barBg: 'bg-orange-400', icon: '🏭' },
  'very high': { color: 'text-red-400', bg: 'bg-red-400/10', barBg: 'bg-red-400', icon: '🔥' },
}

export function CarbonPanel({ carbon }: { carbon: CarbonFootprint }) {
  const cfg = RATING_CONFIG[carbon.rating] || RATING_CONFIG.moderate

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.35 }}
      className="glass-card p-5"
    >
      <div className="mb-4 flex items-center justify-between">
        <h3 className="section-label">Carbon Footprint</h3>
        <div className={`badge ${cfg.bg} ${cfg.color} border-0`}>
          {cfg.icon} {carbon.rating}
        </div>
      </div>

      {/* Main stat */}
      <div className="mb-4 flex items-baseline gap-2">
        <span className={`text-3xl font-bold ${cfg.color}`}>
          {carbon.total_co2_kg.toLocaleString()}
        </span>
        <span className="text-sm text-slate-400">kg CO₂</span>
        <span className="ml-auto text-xs text-slate-500">
          Offset: ₹{carbon.offset_cost_inr.toLocaleString('en-IN')}
        </span>
      </div>

      {/* Legs breakdown */}
      {carbon.legs.length > 0 && (
        <div className="mb-4 space-y-1.5">
          {carbon.legs.map((leg, i) => {
            const maxCo2 = Math.max(...carbon.legs.map((l) => l.co2_kg), 1)
            const pct = (leg.co2_kg / maxCo2) * 100
            return (
              <div key={i} className="flex items-center gap-2">
                <span className="w-5 text-center text-xs">
                  {leg.mode === 'flight' ? '✈️' : '🚌'}
                </span>
                <span className="w-44 truncate text-xs text-slate-400">{leg.leg}</span>
                <div className="flex-1">
                  <div className="h-1 rounded-full bg-surface-2/50 overflow-hidden">
                    <motion.div
                      className={`h-full rounded-full ${cfg.barBg}`}
                      initial={{ width: 0 }}
                      animate={{ width: `${pct}%` }}
                      transition={{ duration: 0.6, delay: 0.1 * i }}
                    />
                  </div>
                </div>
                <span className="w-14 text-right text-xs text-slate-500">
                  {leg.co2_kg} kg
                </span>
              </div>
            )
          })}
        </div>
      )}

      {/* Tips */}
      {carbon.tips.length > 0 && (
        <div className="rounded-lg bg-surface-2/30 p-3">
          <p className="mb-1.5 text-xs font-semibold text-emerald-400">
            💡 Reduction Tips
          </p>
          <ul className="space-y-1">
            {carbon.tips.slice(0, 3).map((tip, i) => (
              <li key={i} className="text-xs text-slate-400 leading-relaxed">
                • {tip}
              </li>
            ))}
          </ul>
        </div>
      )}
    </motion.div>
  )
}
