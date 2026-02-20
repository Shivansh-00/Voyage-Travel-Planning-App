'use client'

export function MapView({ destination }: { destination: string }) {
  return (
    <div className="rounded-xl bg-slate-900 p-6">
      <p className="text-sm text-slate-400">Mapbox GL region</p>
      <p className="text-lg">Destination: {destination}</p>
      <div className="mt-3 h-48 rounded bg-slate-800" />
    </div>
  )
}
