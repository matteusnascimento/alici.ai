"use client"

import { useEffect, useState } from "react"
import { apiGet } from "@/lib/api"

export default function KnowledgePage() {
  const [data, setData] = useState<any[]>([])

  useEffect(() => {
    apiGet<any[]>("/knowledge").then(setData).catch(() => setData([]))
  }, [])

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6">
      <h1 className="text-xl font-bold">Knowledge</h1>
      <p className="mt-2 text-sm">Total: {data.length}</p>
    </section>
  )
}
