'use client'
import { motion, AnimatePresence } from 'framer-motion'

interface StreamingProgressProps {
  visible: boolean
  step: number
  totalSteps: number
  label: string
  progress: number
  agent?: string
}

const AGENT_ICONS: Record<string, string> = {
  intent_extractor: '🧠',
  memory: '💾',
  planner: '🗺️',
  flight: '✈️',
  hotel: '🏨',
  experience: '🎭',
  budget: '💰',
  carbon: '🌿',
  risk: '⚡',
  confidence: '📊',
  validation: '✅',
  done: '🎉',
}

export function StreamingProgress({ visible, step, totalSteps, label, progress, agent }: StreamingProgressProps) {
  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="glass-card p-6"
        >
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="pulse-glow flex h-10 w-10 items-center justify-center rounded-xl bg-brand/10">
                <span className="text-lg">
                  {(agent && AGENT_ICONS[agent]) || '⚙️'}
                </span>
              </div>
              <div>
                <p className="text-sm font-medium text-slate-200">{label}</p>
                <p className="text-xs text-slate-500">
                  Step {step} of {totalSteps}
                </p>
              </div>
            </div>
            <span className="text-sm font-bold gradient-text">{progress}%</span>
          </div>

          <div className="progress-bar">
            <motion.div
              className="progress-bar-fill"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
            />
          </div>

          {/* Agent pipeline pills */}
          <div className="mt-4 flex flex-wrap gap-1.5">
            {Object.entries(AGENT_ICONS)
              .filter(([k]) => k !== 'done')
              .map(([key, icon], idx) => (
                <div
                  key={key}
                  className={`flex items-center gap-1 rounded-full px-2 py-0.5 text-xs transition-all duration-300 ${
                    idx < step
                      ? 'bg-brand/20 text-brand'
                      : idx === step - 1
                      ? 'bg-brand/30 text-brand ring-1 ring-brand/40'
                      : 'bg-surface-2/50 text-slate-500'
                  }`}
                >
                  <span className="text-xs">{icon}</span>
                  <span className="hidden sm:inline">{key.replace('_', ' ')}</span>
                </div>
              ))}
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
