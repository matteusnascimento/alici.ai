import { BillingPage } from "@/features/billing/pages/BillingPage";
import { DashboardLayout } from "@/layouts/DashboardLayout";

export default function BillingRoute() {
  return (
    <DashboardLayout>
      <BillingPage />
    </DashboardLayout>
  );
}
