import { DashboardLayout } from "@/layouts/DashboardLayout";

export default function AdminRoute() {
  return (
    <DashboardLayout>
      <main className="space-y-4 p-2">
        <h1 className="text-2xl font-semibold">Admin</h1>
        <p className="text-sm text-slate-300">Painel administrativo para usuarios, uso e monitoramento.</p>
      </main>
    </DashboardLayout>
  );
}
