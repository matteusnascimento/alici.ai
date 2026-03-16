"use client"

import { FormEvent, useState } from "react"

export default function ChatInput({ onSend }: { onSend: (value: string) => Promise<void> }) {
  const [value, setValue] = useState("")

  async function submit(event: FormEvent) {
    event.preventDefault()
    if (!value.trim()) return
    const payload = value
    setValue("")
    await onSend(payload)
  }

  return (
    <form onSubmit={submit} className="flex gap-2">
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Type a message"
        className="flex-1 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
      />
      <button className="rounded-lg bg-primary px-4 py-2 text-sm text-white">Send</button>
    </form>
  )
}
