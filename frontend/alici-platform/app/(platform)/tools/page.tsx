import { DashboardLayout } from "@/layouts/DashboardLayout";

export default function ToolsRoute() {
  return (
    <DashboardLayout>
      <main className="space-y-4 p-2">
        <h1 className="text-2xl font-semibold">Tools</h1>
        <p className="text-sm text-slate-300">Rota funcional para catálogo e execução de ferramentas.</p>
      </main>
    </DashboardLayout>
  );
}
