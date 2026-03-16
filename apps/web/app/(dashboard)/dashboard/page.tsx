"use client"

import { useEffect, useState } from "react"
import { apiGet } from "@/lib/api"

export default function DashboardPage() {
  const [health, setHealth] = useState("loading")

  useEffect(() => {
    apiGet<{ status: string }>("/health").then((res) => setHealth(res.status)).catch(() => setHealth("error"))
  }, [])

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6">
      <h1 className="text-xl font-bold">Dashboard</h1>
      <p className="mt-2 text-sm text-slate-600">API health: {health}</p>
    </section>
  )
}
