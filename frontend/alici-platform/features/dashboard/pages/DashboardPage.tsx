"use client";

import { useState } from "react";
import { ActivityFeed } from "../components/ActivityFeed";
import { AgentStatusCard } from "../components/AgentStatusCard";
import { CostChart } from "../components/CostChart";
import { DashboardAgentBuilder } from "../components/DashboardAgentBuilder";
import { DashboardChat } from "../components/DashboardChat";
import { DashboardHeader } from "../components/DashboardHeader";
import { NeuralMemoryCard } from "../components/NeuralMemoryCard";
import { QuickActions } from "../components/QuickActions";
import { TokenUsageChart } from "../components/TokenUsageChart";
import { UsageCard } from "../components/UsageCard";
import { useDashboardData } from "../hooks/useDashboardData";
import { DashboardKnowledge } from "../components/DashboardKnowledge";

type Tab = "overview" | "agents" | "chat" | "knowledge";

const TABS: { id: Tab; label: string; emoji: string }[] = [
  { id: "overview",   label: "Overview",       emoji: "📊" },
  { id: "agents",     label: "Agent Builder",  emoji: "🤖" },
  { id: "chat",       label: "Chat",           emoji: "💬" },
  { id: "knowledge",  label: "Knowledge / RAG", emoji: "📚" },
];

export function DashboardPage() {
  const { usage, agents, activity, costs, loading } = useDashboardData();
  const [activeTab, setActiveTab] = useState<Tab>("overview");

  return (
    <div className="flex flex-col gap-6">
      <DashboardHeader />

      {/* ── Tab bar ── */}
      <div className="flex gap-1 rounded-xl border border-slate-800 bg-slate-900/60 p-1">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={`flex flex-1 items-center justify-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition ${
              activeTab === tab.id
                ? "bg-sky-500/20 text-sky-300 ring-1 ring-sky-500/40"
                : "text-slate-400 hover:bg-slate-800 hover:text-slate-200"
            }`}
          >
            <span>{tab.emoji}</span>
            <span className="hidden sm:inline">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* ── Tab content ── */}
      {activeTab === "overview" && (
        <>
          {loading ? (
            <p className="text-sm text-slate-400">Carregando métricas...</p>
          ) : (
            <>
              <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                {usage.tokens   && <UsageCard usage={usage.tokens} />}
                {usage.requests && <UsageCard usage={usage.requests} />}
                {usage.storage  && <UsageCard usage={usage.storage} />}
                {usage.bandwidth && <UsageCard usage={usage.bandwidth} />}
              </section>

              <section className="grid gap-4 xl:grid-cols-2">
                <TokenUsageChart data={usage.tokensHistory} />
                <CostChart data={costs} />
              </section>

              <section className="grid gap-4 xl:grid-cols-2">
                <AgentStatusCard agents={agents} />
                <QuickActions />
              </section>

              <NeuralMemoryCard />
              <ActivityFeed activity={activity} />
            </>
          )}
        </>
      )}

      {activeTab === "agents" && <DashboardAgentBuilder />}

      {activeTab === "chat" && <DashboardChat />}

      {activeTab === "knowledge" && <DashboardKnowledge />}
    </div>
  );
}
