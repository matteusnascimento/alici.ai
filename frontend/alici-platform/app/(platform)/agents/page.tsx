import { AgentsPage } from "@/features/agents/pages/AgentsPage";
import { DashboardLayout } from "@/layouts/DashboardLayout";

export default function AgentsRoute() {
  return (
    <DashboardLayout>
      <AgentsPage />
    </DashboardLayout>
  );
}
