'use client'
import { FormEvent, useState } from 'react'

export function ChatPanel({ onSubmit }: { onSubmit: (message: string) => Promise<void> }) {
  const [value, setValue] = useState('Tokyo')

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    await onSubmit(value)
  }

  return (
    <form onSubmit={handleSubmit} className="rounded-xl bg-slate-900 p-4 shadow-lg">
      <label className="mb-2 block text-sm text-slate-300">Describe your trip request</label>
      <textarea
        className="w-full rounded-md bg-slate-800 p-3"
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />
      <button className="mt-3 rounded-md bg-brand px-4 py-2">Plan trip</button>
    </form>
  )
}
