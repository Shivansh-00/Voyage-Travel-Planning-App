'use client'
import { useState } from 'react'
import { motion } from 'framer-motion'

export function ThemeToggle() {
  const [dark, setDark] = useState(true)
  return (
    <button
      onClick={() => {
        setDark(!dark)
        document.body.classList.toggle('bg-[rgb(var(--surface-0))]')
      }}
      className="group relative flex items-center gap-2 rounded-full bg-surface-2/50 px-3 py-1.5 text-xs text-slate-400 hover:text-slate-200 border border-surface-3/30 hover:border-brand/30 transition-all"
    >
      <motion.span
        animate={{ rotate: dark ? 0 : 180 }}
        transition={{ type: 'spring', stiffness: 300, damping: 20 }}
      >
        {dark ? '🌙' : '☀️'}
      </motion.span>
      {dark ? 'Dark' : 'Light'}
    </button>
  )
}
