import { DashboardLayout } from "@/layouts/DashboardLayout";

export default function ModelsRoute() {
  return (
    <DashboardLayout>
      <main className="space-y-4 p-2">
        <h1 className="text-2xl font-semibold">Models</h1>
        <p className="text-sm text-slate-300">Rota funcional para gerenciamento de modelos em `/api/models`.</p>
      </main>
    </DashboardLayout>
  );
}
