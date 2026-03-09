import type { ReactNode } from "react";
import { DashboardLayout } from "@/layouts/DashboardLayout";

export default function PlatformLayout({ children }: { children: ReactNode }) {
  return <DashboardLayout>{children}</DashboardLayout>;
}
