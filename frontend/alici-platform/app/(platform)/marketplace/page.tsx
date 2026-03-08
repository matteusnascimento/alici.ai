import { DashboardLayout } from "@/layouts/DashboardLayout";

export default function MarketplaceRoute() {
  return (
    <DashboardLayout>
      <main className="space-y-4 p-2">
        <h1 className="text-2xl font-semibold">Marketplace</h1>
        <p className="text-sm text-slate-300">Rota funcional para listagem de agentes e plugins.</p>
      </main>
    </DashboardLayout>
  );
}
