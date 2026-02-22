'use client'
import { motion } from 'framer-motion'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts'
import { CostBreakdown } from '@/types/travel'

const SEGMENTS = [
  { key: 'flights_estimated', label: 'Flights', icon: '✈️', color: '#6D5BFF' },
  { key: 'accommodation_estimated', label: 'Hotels', icon: '🏨', color: '#22D3EE' },
  { key: 'activities_estimated', label: 'Activities', icon: '🎭', color: '#34D399' },
  { key: 'transport_estimated', label: 'Transport', icon: '🚌', color: '#F59E0B' },
]

export function BudgetChart({ breakdown }: { breakdown: CostBreakdown }) {
  const data = SEGMENTS.map(({ key, label, color }) => ({
    name: label,
    value: (breakdown as Record<string, number>)[key] ?? 0,
    color,
  })).filter((d) => d.value > 0)

  const total = breakdown.total_estimated

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="glass-card p-5"
    >
      <h2 className="section-label mb-1">Cost Breakdown</h2>
      <p className="mb-4 text-2xl font-bold gradient-text">
        ₹{total.toLocaleString('en-IN')}
      </p>

      <div className="flex items-center gap-6">
        {/* Donut Chart */}
        <div className="relative w-36 h-36 flex-shrink-0">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                dataKey="value"
                cx="50%"
                cy="50%"
                innerRadius={38}
                outerRadius={60}
                paddingAngle={3}
                animationBegin={200}
                animationDuration={800}
              >
                {data.map((entry, index) => (
                  <Cell
                    key={index}
                    fill={entry.color}
                    stroke="transparent"
                  />
                ))}
              </Pie>
              <Tooltip
                formatter={(v: number) => `₹${v.toLocaleString('en-IN')}`}
                contentStyle={{
                  background: 'rgba(15, 23, 42, 0.95)',
                  border: '1px solid rgba(51, 65, 85, 0.4)',
                  borderRadius: '8px',
                  fontSize: '12px',
                  color: '#e2e8f0',
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Legend */}
        <div className="flex-1 space-y-2.5">
          {SEGMENTS.map(({ key, label, icon, color }) => {
            const value = (breakdown as Record<string, number>)[key] ?? 0
            const pct = total > 0 ? Math.round((value / total) * 100) : 0
            return (
              <div key={key} className="flex items-center gap-2">
                <div
                  className="h-2.5 w-2.5 rounded-full flex-shrink-0"
                  style={{ backgroundColor: color }}
                />
                <span className="text-xs text-slate-400 flex-1">
                  {icon} {label}
                </span>
                <span className="text-xs font-medium text-slate-300">
                  ₹{value.toLocaleString('en-IN')}
                </span>
                <span className="w-8 text-right text-[10px] text-slate-500">{pct}%</span>
              </div>
            )
          })}
        </div>
      </div>
    </motion.div>
  )
}
