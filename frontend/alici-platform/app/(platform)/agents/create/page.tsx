import Link from "next/link";
import { DashboardLayout } from "@/layouts/DashboardLayout";

export default function AgentsCreateRoute() {
  return (
    <DashboardLayout>
      <main className="space-y-4 p-2">
        <h1 className="text-2xl font-semibold">Create Agent</h1>
        <p className="text-sm text-slate-300">Use o endpoint `POST /api/agents/create` para criar um novo agente.</p>
        <Link href="/agents" className="inline-block rounded-lg bg-sky-500 px-4 py-2 text-sm font-medium text-white hover:bg-sky-400">
          Back to Agents
        </Link>
      </main>
    </DashboardLayout>
  );
}
