import { DashboardLayout } from "@/layouts/DashboardLayout";

export default function KnowledgeRoute() {
  return (
    <DashboardLayout>
      <main className="space-y-4 p-2">
        <h1 className="text-2xl font-semibold">Knowledge Base</h1>
        <p className="text-sm text-slate-300">Rota funcional para upload e consulta em `/api/knowledge/*`.</p>
      </main>
    </DashboardLayout>
  );
}
