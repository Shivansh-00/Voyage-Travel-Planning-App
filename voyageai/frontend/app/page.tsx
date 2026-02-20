'use client'
import { ChatPanel } from '@/components/ChatPanel'
import { Timeline } from '@/components/Timeline'
import { BudgetChart } from '@/components/BudgetChart'
import { MapView } from '@/components/MapView'
import { LoadingSkeleton } from '@/components/LoadingSkeleton'
import { ThemeToggle } from '@/components/ThemeToggle'
import { useTravelPlan } from '@/hooks/useTravelPlan'

export default function HomePage() {
  const { data, loading, generate } = useTravelPlan()

  return (
    <main className="mx-auto min-h-screen max-w-6xl p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-semibold">VoyageAI – Autonomous Travel Intelligence Engine</h1>
        <ThemeToggle />
      </div>
      <div className="grid gap-6 md:grid-cols-2">
        <ChatPanel onSubmit={generate} />
        {loading ? <LoadingSkeleton /> : data && <MapView destination={data.itinerary[0]?.location ?? 'Unknown'} />}
      </div>
      <div className="mt-6 grid gap-6 md:grid-cols-2">
        {data ? <Timeline items={data.itinerary} /> : <LoadingSkeleton />}
        {data ? <BudgetChart items={data.itinerary} /> : <LoadingSkeleton />}
      </div>
      {data && <p className="mt-4 text-sm text-slate-400">{data.optimization_summary}</p>}
    </main>
  )
}
