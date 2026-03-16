"use client"

import { useEffect, useState } from "react"
import { apiGet } from "@/lib/api"

export default function SettingsPage() {
  const [health, setHealth] = useState("loading")

  useEffect(() => {
    apiGet<{ status: string }>("/health").then((r) => setHealth(r.status)).catch(() => setHealth("error"))
  }, [])

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6">
      <h1 className="text-xl font-bold">Settings</h1>
      <p className="mt-2 text-sm">Connection: {health}</p>
    </section>
  )
}
