import { DashboardLayout } from "@/layouts/DashboardLayout";

export default function KnowledgeRoute() {
  /**
   * Function: KnowledgeRoute
   * Description: Render the canonical knowledge module route.
   * Parameters:
   * Returns:
   *   Knowledge route page component.
   */
  return (
    <DashboardLayout>
      <main className="space-y-4 p-2">
        <h1 className="text-2xl font-semibold">Knowledge Base</h1>
        <p className="text-sm text-slate-300">Module under development.</p>
      </main>
    </DashboardLayout>
  );
}
