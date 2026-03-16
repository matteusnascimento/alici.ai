import { ReactNode } from "react"

import Sidebar from "@/components/sidebar"
import TopNavigation from "@/components/top-navigation"

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex w-full flex-col">
        <TopNavigation />
        <main className="p-6">{children}</main>
      </div>
    </div>
  )
}
