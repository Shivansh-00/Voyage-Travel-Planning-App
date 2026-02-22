'use client'
import { motion } from 'framer-motion'

export function LoadingSkeleton({ rows = 3, className = '' }: { rows?: number; className?: string }) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className={`glass-card p-5 space-y-3 ${className}`}
    >
      <div className="shimmer h-4 w-24 rounded" />
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="space-y-2">
          <div className="shimmer h-3 rounded" style={{ width: `${85 - i * 10}%` }} />
          <div className="shimmer h-3 rounded" style={{ width: `${70 - i * 8}%` }} />
        </div>
      ))}
      <div className="shimmer h-3 w-1/2 rounded" />
    </motion.div>
  )
}

export function MapSkeleton() {
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card overflow-hidden">
      <div className="shimmer h-[280px] w-full" />
      <div className="p-5 space-y-3">
        <div className="shimmer h-3 w-20 rounded" />
        <div className="shimmer h-4 w-3/4 rounded" />
        <div className="shimmer h-3 w-16 rounded" />
        <div className="flex gap-2">
          <div className="shimmer h-6 w-32 rounded-full" />
          <div className="shimmer h-6 w-28 rounded-full" />
        </div>
      </div>
    </motion.div>
  )
}
