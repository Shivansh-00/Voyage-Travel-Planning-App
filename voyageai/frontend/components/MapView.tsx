'use client'
import { useEffect, useState, useMemo } from 'react'
import { motion } from 'framer-motion'
import { TransportPlan, StayRecommendation, VisaInformation } from '@/types/travel'

// City coordinates for the interactive map
const CITY_COORDS: Record<string, [number, number]> = {
  delhi: [28.6139, 77.209], 'new delhi': [28.6139, 77.209],
  mumbai: [19.076, 72.8777], bangalore: [12.9716, 77.5946],
  chennai: [13.0827, 80.2707], kolkata: [22.5726, 88.3639],
  hyderabad: [17.385, 78.4867], jaipur: [26.9124, 75.7873],
  goa: [15.2993, 74.124], kochi: [9.9312, 76.2673],
  varanasi: [25.3176, 82.9739], udaipur: [24.5854, 73.7125],
  shimla: [31.1048, 77.1734], manali: [32.2396, 77.1887],
  rishikesh: [30.0869, 78.2676], leh: [34.1526, 77.5771],
  srinagar: [34.0837, 74.7973], amritsar: [31.634, 74.8723],
  agra: [27.1767, 78.0081],
  tokyo: [35.6762, 139.6503], kyoto: [35.0116, 135.7681],
  osaka: [34.6937, 135.5023], paris: [48.8566, 2.3522],
  london: [51.5074, -0.1278], 'new york': [40.7128, -74.006],
  dubai: [25.2048, 55.2708], singapore: [1.3521, 103.8198],
  bangkok: [13.7563, 100.5018], bali: [-8.3405, 115.092],
  rome: [41.9028, 12.4964], barcelona: [41.3874, 2.1686],
  amsterdam: [52.3676, 4.9041], berlin: [52.52, 13.405],
  sydney: [-33.8688, 151.2093], seoul: [37.5665, 126.978],
  istanbul: [41.0082, 28.9784], 'kuala lumpur': [3.139, 101.6869],
  hanoi: [21.0278, 105.8342], prague: [50.0755, 14.4378],
  budapest: [47.4979, 19.0402], lisbon: [38.7223, -9.1393],
  athens: [37.9838, 23.7275], cairo: [30.0444, 31.2357],
  'cape town': [-33.9249, 18.4241], maldives: [3.2028, 73.2207],
  phuket: [7.8804, 98.3923], kathmandu: [27.7172, 85.324],
  colombo: [6.9271, 79.8612],
}

function getCoords(city: string): [number, number] | null {
  return CITY_COORDS[city.toLowerCase().trim()] || null
}

/** Calculate appropriate zoom level from lat/lng bounds. */
function calculateZoom(coords: [number, number][]): number {
  if (coords.length <= 1) return 10
  const lats = coords.map((c) => c[0])
  const lngs = coords.map((c) => c[1])
  const latSpan = Math.max(...lats) - Math.min(...lats)
  const lngSpan = Math.max(...lngs) - Math.min(...lngs)
  const maxSpan = Math.max(latSpan, lngSpan)
  // Rough mapping: 360° → zoom 1, 180° → 2, 90° → 3, ...
  if (maxSpan <= 0.05) return 12
  if (maxSpan <= 0.5) return 10
  if (maxSpan <= 2) return 8
  if (maxSpan <= 5) return 6
  if (maxSpan <= 15) return 5
  if (maxSpan <= 40) return 4
  if (maxSpan <= 80) return 3
  return 2
}

interface MapViewProps {
  route: TransportPlan
  stays: StayRecommendation[]
  visa: VisaInformation
}

export function MapView({ route, stays, visa }: MapViewProps) {
  const [MapComponent, setMapComponent] = useState<any>(null)
  const [loadError, setLoadError] = useState(false)

  useEffect(() => {
    let cancelled = false
    Promise.all([import('leaflet'), import('react-leaflet')])
      .then(([L, RL]) => {
        if (cancelled) return
        delete (L.Icon.Default.prototype as any)._getIconUrl
        L.Icon.Default.mergeOptions({
          iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
          iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
          shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
        })
        setMapComponent({
          L,
          MapContainer: RL.MapContainer,
          TileLayer: RL.TileLayer,
          Marker: RL.Marker,
          Popup: RL.Popup,
          Polyline: RL.Polyline,
        })
      })
      .catch(() => {
        if (!cancelled) setLoadError(true)
      })
    return () => { cancelled = true }
  }, [])

  const routeCities = useMemo(
    () => route.route_order.filter((c, i, arr) => c !== arr[0] || i === 0),
    [route.route_order],
  )
  const routeCoords = useMemo(
    () => routeCities.map((c) => getCoords(c)).filter(Boolean) as [number, number][],
    [routeCities],
  )
  const center: [number, number] = useMemo(
    () =>
      routeCoords.length > 0
        ? [
            routeCoords.reduce((s, c) => s + c[0], 0) / routeCoords.length,
            routeCoords.reduce((s, c) => s + c[1], 0) / routeCoords.length,
          ]
        : [20, 78],
    [routeCoords],
  )
  const zoom = useMemo(() => calculateZoom(routeCoords), [routeCoords])

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-card overflow-hidden"
    >
      {/* Interactive Map */}
      <div className="relative h-[280px] w-full">
        {loadError ? (
          <div className="flex h-full items-center justify-center bg-surface-1 text-sm text-slate-500">
            Map could not be loaded
          </div>
        ) : MapComponent ? (
          <MapComponent.MapContainer
            center={center}
            zoom={zoom}
            className="h-full w-full"
            scrollWheelZoom={false}
          >
            <MapComponent.TileLayer
              attribution='&copy; <a href="https://carto.com">CARTO</a>'
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            />
            {routeCoords.map((pos, i) => (
              <MapComponent.Marker key={i} position={pos}>
                <MapComponent.Popup>
                  <div className="text-sm">
                    <strong>{routeCities[i]}</strong>
                    {stays.find((s) => s.city.toLowerCase() === routeCities[i].toLowerCase()) && (
                      <p className="mt-1 text-xs">
                        🏨 {stays.find((s) => s.city.toLowerCase() === routeCities[i].toLowerCase())?.stay_type}
                      </p>
                    )}
                  </div>
                </MapComponent.Popup>
              </MapComponent.Marker>
            ))}
            {routeCoords.length > 1 && (
              <MapComponent.Polyline
                positions={routeCoords}
                pathOptions={{ color: '#6D5BFF', weight: 2, opacity: 0.7, dashArray: '8, 8' }}
              />
            )}
          </MapComponent.MapContainer>
        ) : (
          <div className="flex h-full items-center justify-center bg-surface-1">
            <div className="shimmer h-full w-full" />
          </div>
        )}
      </div>

      {/* Info panel below map */}
      <div className="p-5 space-y-4">
        <div>
          <h3 className="section-label mb-2">Route</h3>
          <div className="flex flex-wrap items-center gap-1.5 text-sm text-slate-300">
            {route.route_order.map((city, i) => (
              <span key={i} className="flex items-center gap-1.5">
                {i > 0 && <span className="text-brand">→</span>}
                <span className="rounded-md bg-surface-2/50 px-2 py-0.5 text-xs font-medium">{city}</span>
              </span>
            ))}
          </div>
        </div>

        {route.recommended_passes.length > 0 && (
          <div>
            <h3 className="section-label mb-2">Transport Passes</h3>
            <div className="flex flex-wrap gap-1.5">
              {route.recommended_passes.map((p, i) => (
                <span key={i} className="badge badge-cyan">🎫 {p}</span>
              ))}
            </div>
          </div>
        )}

        {stays.length > 0 && (
          <div>
            <h3 className="section-label mb-2">Accommodations</h3>
            <div className="grid gap-2 sm:grid-cols-2">
              {stays.map((s, i) => (
                <div key={i} className="flex items-center justify-between rounded-lg bg-surface-2/30 px-3 py-2">
                  <div>
                    <p className="text-sm font-medium text-slate-200">{s.city}</p>
                    <p className="text-xs text-slate-500">{s.stay_type}</p>
                  </div>
                  <span className="text-sm font-semibold text-emerald-400">
                    ₹{s.budget_per_night_inr.toLocaleString('en-IN')}
                    <span className="text-xs text-slate-500">/night</span>
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div>
          <h3 className="section-label mb-2">Visa Information</h3>
          <div className={`rounded-lg p-3 text-sm ${
            visa.required
              ? 'bg-amber-400/5 border border-amber-400/20 text-amber-300'
              : 'bg-emerald-400/5 border border-emerald-400/20 text-emerald-300'
          }`}>
            <span className="font-medium">
              {visa.required ? '⚠️ Visa required' : '✅ No visa required'}
            </span>
            <p className="mt-1 text-xs opacity-80">{visa.details}</p>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
