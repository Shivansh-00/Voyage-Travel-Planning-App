'use client'
import { useState } from 'react'

export function ThemeToggle() {
  const [dark, setDark] = useState(true)
  return (
    <button
      onClick={() => {
        setDark(!dark)
        document.body.classList.toggle('bg-slate-950')
      }}
      className="rounded-lg border border-slate-600 px-3 py-1 text-sm"
    >
      {dark ? 'Light' : 'Dark'} mode
    </button>
  )
}
