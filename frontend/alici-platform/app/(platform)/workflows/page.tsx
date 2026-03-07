import { WorkflowsPage } from "@/features/workflows/pages/WorkflowsPage";
import { DashboardLayout } from "@/layouts/DashboardLayout";

export default function WorkflowsRoute() {
  return (
    <DashboardLayout>
      <WorkflowsPage />
    </DashboardLayout>
  );
}
