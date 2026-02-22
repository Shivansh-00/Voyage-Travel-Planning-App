'use client'
import { motion } from 'framer-motion'
import { DayItinerary } from '@/types/travel'

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.08 } },
}

const item = {
  hidden: { opacity: 0, x: -20 },
  show: { opacity: 1, x: 0, transition: { type: 'spring', stiffness: 300, damping: 30 } },
}

export function Timeline({ items }: { items: DayItinerary[] }) {
  // Group by city for visual breaks
  let currentCity = ''

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-2">
      <h2 className="section-label mb-3">Day-by-Day Itinerary</h2>
      {items.map((day) => {
        const isNewCity = day.city !== currentCity
        currentCity = day.city
        return (
          <div key={`day-${day.day}`}>
            {isNewCity && (
              <motion.div variants={item} className="mt-3 mb-2 flex items-center gap-2">
                <div className="h-px flex-1 bg-gradient-to-r from-brand/30 to-transparent" />
                <span className="text-xs font-bold uppercase tracking-wider text-brand">📍 {day.city}</span>
                <div className="h-px flex-1 bg-gradient-to-l from-brand/30 to-transparent" />
              </motion.div>
            )}
            <motion.div variants={item} className="glass-card group relative p-4">
              {/* Day connector line */}
              <div className="absolute -left-px top-0 bottom-0 w-0.5 bg-gradient-to-b from-brand/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand/10 text-xs font-bold text-brand">
                    {day.day}
                  </div>
                  <div>
                    <p className="text-xs text-slate-500">{day.city}</p>
                    {day.weather_note && (
                      <p className="text-[10px] text-slate-500 mt-0.5">{day.weather_note}</p>
                    )}
                  </div>
                </div>
                <span className="badge badge-emerald">
                  ₹{day.estimated_cost_inr.toLocaleString('en-IN')}
                </span>
              </div>

              <ul className="mt-3 space-y-1.5 pl-11">
                {day.activities.map((act, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                    <span className="mt-1 h-1.5 w-1.5 rounded-full bg-brand/50 flex-shrink-0" />
                    <span>{act}</span>
                  </li>
                ))}
              </ul>
            </motion.div>
          </div>
        )
      })}
    </motion.div>
  )
}
