"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/Card";
import { api } from "@/services/api";

interface PlatformStats {
  chats: number;
  agents: number;
  documents: number;
  tokens: number;
}

interface ApiEnvelope<T> {
  status: "success" | "error";
  data: T;
  error: string | null;
}

const quickActions = [
  { href: "/agents/create", label: "Create Agent" },
  { href: "/knowledge", label: "Upload Knowledge" },
  { href: "/chat", label: "Start Chat" }
] as const;

export default function PlatformHomePage() {
  const [stats, setStats] = useState<PlatformStats>({
    chats: 0,
    agents: 0,
    documents: 0,
    tokens: 0
  });

  useEffect(() => {
    let active = true;

    async function loadPlatformStats() {
      /**
       * Function: loadPlatformStats
       * Description: Load high-level platform metrics from the backend overview endpoint.
       * Parameters:
       * Returns:
       *   Promise that resolves after local state is updated.
       */
      try {
        const response = await api.get<ApiEnvelope<{ stats?: Record<string, number> }>>("/platform/overview");
        const payload = response.data?.data ?? {};

        if (!active) return;

        setStats({
          chats: Number(payload?.stats?.total_requests ?? 0),
          agents: Number(payload?.stats?.total_agents ?? 0),
          documents: Number(payload?.stats?.total_knowledge_docs ?? 0),
          tokens: Number(payload?.stats?.current_month_tokens ?? 0)
        });
      } catch {
        // Keep defaults if backend overview is unavailable.
      }
    }

    void loadPlatformStats();
    return () => {
      active = false;
    };
  }, []);

  return (
      <section className="space-y-8">
        <header className="flex items-center justify-between">
          <h1 className="text-3xl font-semibold">Dashboard</h1>
          <Link
            href="/agents/create"
            className="rounded-lg bg-sky-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-sky-400"
          >
            Create Agent
          </Link>
        </header>

        <div className="grid gap-6 sm:grid-cols-2 xl:grid-cols-4">
          <Card className="rounded-2xl">
            <CardContent className="p-1">
              <p className="text-sm text-slate-400">Chats</p>
              <h2 className="text-3xl font-bold">{stats.chats.toLocaleString()}</h2>
            </CardContent>
          </Card>

          <Card className="rounded-2xl">
            <CardContent className="p-1">
              <p className="text-sm text-slate-400">Agents Active</p>
              <h2 className="text-3xl font-bold">{stats.agents.toLocaleString()}</h2>
            </CardContent>
          </Card>

          <Card className="rounded-2xl">
            <CardContent className="p-1">
              <p className="text-sm text-slate-400">Documents</p>
              <h2 className="text-3xl font-bold">{stats.documents.toLocaleString()}</h2>
            </CardContent>
          </Card>

          <Card className="rounded-2xl">
            <CardContent className="p-1">
              <p className="text-sm text-slate-400">Tokens Used</p>
              <h2 className="text-3xl font-bold">{stats.tokens.toLocaleString()}</h2>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {quickActions.map((action) => (
            <Card key={action.href} className="rounded-2xl">
              <CardContent className="flex flex-col gap-4 p-1">
                <h3 className="text-lg font-semibold">{action.label}</h3>
                <p className="text-sm text-slate-400">
                  {action.label === "Create Agent" && "Build a custom AI agent with tools and memory."}
                  {action.label === "Upload Knowledge" && "Add documents to your knowledge base."}
                  {action.label === "Start Chat" && "Open a new AI conversation."}
                </p>
                <Link href={action.href}>
                  <span className="inline-flex rounded-lg bg-sky-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-sky-400">
                    {action.label}
                  </span>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>
  );
}
