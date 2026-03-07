import { IntegrationsPage } from "@/features/integrations/pages/IntegrationsPage";
import { DashboardLayout } from "@/layouts/DashboardLayout";

export default function IntegrationsRoute() {
  return (
    <DashboardLayout>
      <IntegrationsPage />
    </DashboardLayout>
  );
}
