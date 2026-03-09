"use client";

import { ActivityFeed } from "../components/ActivityFeed";
import { AgentStatusCard } from "../components/AgentStatusCard";
import { CostChart } from "../components/CostChart";
import { DashboardHeader } from "../components/DashboardHeader";
import { NeuralMemoryCard } from "../components/NeuralMemoryCard";
import { QuickActions } from "../components/QuickActions";
import { TokenUsageChart } from "../components/TokenUsageChart";
import { UsageCard } from "../components/UsageCard";
import { useDashboardData } from "../hooks/useDashboardData";

export function DashboardPage() {
  const { usage, agents, activity, costs, loading } = useDashboardData();

  if (loading || !usage.tokens || !usage.requests || !usage.storage || !usage.bandwidth) {
    return <div className="p-4 text-sm text-slate-300">Loading dashboard...</div>;
  }

  return (
    <div className="flex flex-col gap-6">
      <DashboardHeader />

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <UsageCard usage={usage.tokens} />
        <UsageCard usage={usage.requests} />
        <UsageCard usage={usage.storage} />
        <UsageCard usage={usage.bandwidth} />
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
    </div>
  );
}
