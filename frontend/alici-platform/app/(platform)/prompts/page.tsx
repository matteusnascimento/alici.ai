import { DashboardLayout } from "@/layouts/DashboardLayout";

export default function PromptsRoute() {
  return (
    <DashboardLayout>
      <main className="space-y-4 p-2">
        <h1 className="text-2xl font-semibold">Prompts</h1>
        <p className="text-sm text-slate-300">Hub de prompts do AI Studio com rota ativa.</p>
      </main>
    </DashboardLayout>
  );
}
