import { DashboardLayout } from "@/layouts/DashboardLayout";

export default function ModelsRoute() {
  /**
   * Function: ModelsRoute
   * Description: Render models module route while feature work is still ongoing.
   * Parameters:
   * Returns:
   *   Models route page component.
   */
  return (
    <DashboardLayout>
      <main className="space-y-4 p-2">
        <h1 className="text-2xl font-semibold">Models</h1>
        <p className="text-sm text-slate-300">Module under development.</p>
      </main>
    </DashboardLayout>
  );
}
