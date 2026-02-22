'use client'
import { motion, AnimatePresence } from 'framer-motion'
import { ChatPanel } from '@/components/ChatPanel'
import { Timeline } from '@/components/Timeline'
import { BudgetChart } from '@/components/BudgetChart'
import { MapView } from '@/components/MapView'
import { LoadingSkeleton, MapSkeleton } from '@/components/LoadingSkeleton'
import { ThemeToggle } from '@/components/ThemeToggle'
import { StreamingProgress } from '@/components/StreamingProgress'
import { ConfidencePanel } from '@/components/ConfidencePanel'
import { CarbonPanel } from '@/components/CarbonPanel'
import { WeatherPanel } from '@/components/WeatherPanel'
import { ErrorBoundary } from '@/components/ErrorBoundary'
import { useTravelPlan } from '@/hooks/useTravelPlan'

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08, duration: 0.5, ease: [0.22, 1, 0.36, 1] },
  }),
}

export default function HomePage() {
  const { data, loading, error, stream, generate } = useTravelPlan()
  const plan = data?.plan
  const intent = data?.intent

  return (
    <main className="mx-auto min-h-screen max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      {/* ─── Header ─────────────────────────────────────────── */}
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8 flex items-center justify-between"
      >
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl gradient-brand">
            <span className="text-lg">✈️</span>
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-100 sm:text-2xl">VoyageAI</h1>
            <p className="text-[11px] text-slate-500 tracking-wider uppercase">
              Autonomous Travel Intelligence
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {data?.processing_time_ms && (
            <span className="hidden sm:inline text-[11px] text-slate-600">
              {data.processing_time_ms}ms
            </span>
          )}
          <ThemeToggle />
        </div>
      </motion.header>

      {/* ─── Input + Map ────────────────────────────────────── */}
      <div className="grid gap-6 lg:grid-cols-2">
        <ChatPanel onSubmit={generate} loading={loading} />
        <ErrorBoundary>
          <AnimatePresence mode="wait">
            {loading && !plan ? (
              <MapSkeleton key="skeleton" />
            ) : plan ? (
              <MapView
                key="map"
                route={plan.transport_plan}
                stays={plan.stay_recommendations}
                visa={plan.visa_information}
              />
            ) : (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="glass-card flex items-center justify-center p-12"
              >
                <div className="text-center">
                  <span className="text-4xl">🌍</span>
                  <p className="mt-3 text-sm text-slate-500">
                    Describe your dream trip to get started
                  </p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </ErrorBoundary>
      </div>

      {/* ─── Error Banner ───────────────────────────────────── */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="mt-4 rounded-xl bg-red-500/5 border border-red-500/20 px-5 py-3 text-sm text-red-300"
          >
            <strong className="font-semibold">Error:</strong> {error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* ─── Streaming Progress ─────────────────────────────── */}
      {loading && stream && (
        <div className="mt-6">
          <StreamingProgress
            visible={loading}
            step={stream.step}
            totalSteps={stream.totalSteps}
            label={stream.label}
            progress={stream.progress}
            agent={stream.agent}
          />
        </div>
      )}

      {/* ─── Intent Summary ─────────────────────────────────── */}
      <AnimatePresence>
        {intent && (
          <motion.div
            variants={fadeUp}
            initial="hidden"
            animate="visible"
            custom={0}
            className="glass-card mt-6 p-5"
          >
            <h2 className="section-label mb-3">Extracted Intent</h2>
            <div className="grid gap-x-6 gap-y-2 text-sm sm:grid-cols-2 lg:grid-cols-4">
              {[
                { label: 'Destinations', value: intent.destinations.join(', ') },
                { label: 'Duration', value: `${intent.duration_days} days` },
                {
                  label: 'Budget',
                  value: intent.budget_total_inr
                    ? `₹${intent.budget_total_inr.toLocaleString('en-IN')}`
                    : '—',
                },
                { label: 'Travelers', value: String(intent.traveler_count) },
                ...(intent.travel_month
                  ? [
                      {
                        label: 'Month',
                        value: `${intent.travel_month}${intent.travel_year ? ` ${intent.travel_year}` : ''}`,
                      },
                    ]
                  : []),
                ...(intent.trip_type.length > 0
                  ? [{ label: 'Trip type', value: intent.trip_type.join(', ') }]
                  : []),
                ...(intent.interests.length > 0
                  ? [{ label: 'Interests', value: intent.interests.join(', ') }]
                  : []),
                ...(intent.origin_city ? [{ label: 'Origin', value: intent.origin_city }] : []),
              ].map(({ label, value }) => (
                <div key={label}>
                  <span className="text-slate-500 text-xs">{label}</span>
                  <p className="font-medium text-slate-200">{value || '—'}</p>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ─── Summary + Route ────────────────────────────────── */}
      {plan && (
        <motion.div
          variants={fadeUp}
          initial="hidden"
          animate="visible"
          custom={1}
          className="glass-card mt-4 p-5"
        >
          <p className="text-sm font-medium text-slate-200">{plan.summary}</p>
          <p className="mt-1 text-xs text-slate-500">{plan.route_strategy}</p>
        </motion.div>
      )}

      {/* ─── Itinerary + Budget ─────────────────────────────── */}
      <AnimatePresence>
        {(loading || plan) && (
          <motion.div
            variants={fadeUp}
            initial="hidden"
            animate="visible"
            custom={2}
            className="mt-6 grid gap-6 lg:grid-cols-5"
          >
            <div className="lg:col-span-3">
              <ErrorBoundary>
                {loading && !plan ? <LoadingSkeleton rows={5} /> : plan ? <Timeline items={plan.day_by_day_itinerary} /> : null}
              </ErrorBoundary>
            </div>
            <div className="space-y-6 lg:col-span-2">
              <ErrorBoundary>
                {loading && !plan ? <LoadingSkeleton rows={4} /> : plan ? <BudgetChart breakdown={plan.cost_breakdown} /> : null}
              </ErrorBoundary>
              <ErrorBoundary>
                {plan?.carbon_footprint && <CarbonPanel carbon={plan.carbon_footprint} />}
              </ErrorBoundary>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ─── Intelligence Panels ────────────────────────────── */}
      {data && (
        <motion.div
          variants={fadeUp}
          initial="hidden"
          animate="visible"
          custom={3}
          className="mt-6 grid gap-6 md:grid-cols-2"
        >
          <ErrorBoundary>
            <ConfidencePanel scores={data.confidence} />
          </ErrorBoundary>
          <ErrorBoundary>
            {plan?.weather_insights && plan.weather_insights.length > 0 && (
              <WeatherPanel insights={plan.weather_insights} />
            )}
          </ErrorBoundary>
        </motion.div>
      )}

      {/* ─── Remote Work Spots ──────────────────────────────── */}
      {plan && plan.remote_work_friendly_spots.length > 0 && (
        <motion.div
          variants={fadeUp}
          initial="hidden"
          animate="visible"
          custom={4}
          className="glass-card mt-6 p-5"
        >
          <h2 className="section-label mb-3">💻 Remote Work Spots</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {plan.remote_work_friendly_spots.map((spot, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.1 * i }}
                className="rounded-xl bg-surface-2/30 p-3"
              >
                <p className="text-sm font-semibold text-slate-200">{spot.city}</p>
                <ul className="mt-1.5 space-y-1">
                  {spot.recommendations.map((r, j) => (
                    <li key={j} className="text-xs text-slate-400 flex items-start gap-1.5">
                      <span className="text-cyan-400 mt-0.5">•</span> {r}
                    </li>
                  ))}
                </ul>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* ─── Score Badges ───────────────────────────────────── */}
      {data && (
        <motion.div
          variants={fadeUp}
          initial="hidden"
          animate="visible"
          custom={5}
          className="mt-6 flex flex-wrap items-center gap-3"
        >
          <span className="badge badge-emerald">
            ✨ Optimization: {plan?.optimization_score ?? 0}/10
          </span>
          <span className="badge badge-amber">
            ⚡ Risk: {data.risk_score}/10
          </span>
          {data.confidence?.overall > 0 && (
            <span className="badge badge-brand">
              🎯 Confidence: {Math.round(data.confidence.overall * 100)}%
            </span>
          )}
          <span className="text-xs text-slate-500 ml-auto">{data.optimization_summary}</span>
        </motion.div>
      )}

      {/* ─── Agent Logs ─────────────────────────────────────── */}
      {data && data.agent_logs.length > 0 && (
        <motion.details
          variants={fadeUp}
          initial="hidden"
          animate="visible"
          custom={6}
          className="mt-6 mb-8"
        >
          <summary className="cursor-pointer text-xs text-slate-600 hover:text-slate-400 transition-colors">
            🔍 Agent Logs ({data.agent_logs.length} entries)
          </summary>
          <div className="mt-2 max-h-48 overflow-y-auto glass-card p-4 text-xs text-slate-500 font-mono space-y-1">
            {data.agent_logs.map((log, i) => (
              <div key={i} className="hover:text-slate-300 transition-colors">
                {log}
              </div>
            ))}
          </div>
        </motion.details>
      )}
    </main>
  )
}
