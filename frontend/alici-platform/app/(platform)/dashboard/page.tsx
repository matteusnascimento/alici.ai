import { DashboardPage } from "@/features/dashboard/pages/DashboardPage";
import { DashboardLayout } from "@/layouts/DashboardLayout";

export default function DashboardRoute() {
  return (
    <DashboardLayout>
      <DashboardPage />
    </DashboardLayout>
  );
}
