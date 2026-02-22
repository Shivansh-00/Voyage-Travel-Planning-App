import './globals.css'
import { ReactNode } from 'react'

export const metadata = {
  title: 'VoyageAI — Autonomous Travel Intelligence',
  description: 'AI-powered travel planning with multi-agent intelligence',
}

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />
      </head>
      <body className="font-sans antialiased">{children}</body>
    </html>
  )
}
