import { DashboardLayout } from "@/layouts/DashboardLayout";

export default function ToolsRoute() {
  /**
   * Function: ToolsRoute
   * Description: Render tools module route while feature work is still ongoing.
   * Parameters:
   * Returns:
   *   Tools route page component.
   */
  return (
    <DashboardLayout>
      <main className="space-y-4 p-2">
        <h1 className="text-2xl font-semibold">Tools</h1>
        <p className="text-sm text-slate-300">Module under development.</p>
      </main>
    </DashboardLayout>
  );
}
