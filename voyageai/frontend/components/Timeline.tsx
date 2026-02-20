'use client'
import { motion } from 'framer-motion'
import { ItineraryItem } from '@/types/travel'

export function Timeline({ items }: { items: ItineraryItem[] }) {
  return (
    <div className="space-y-3">
      {items.map((item) => (
        <motion.div key={`${item.day}-${item.activity}`} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="rounded-lg bg-slate-900 p-3">
          <p className="text-xs text-slate-400">Day {item.day}</p>
          <p>{item.activity}</p>
          <p className="text-sm text-slate-400">${item.estimated_cost}</p>
        </motion.div>
      ))}
    </div>
  )
}
