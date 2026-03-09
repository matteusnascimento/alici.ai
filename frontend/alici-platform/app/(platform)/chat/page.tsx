import { DashboardLayout } from "@/layouts/DashboardLayout";
import { ChatWorkspace } from "@/components/chat/ChatWorkspace";

export default function ChatRoute() {
  return (
    <DashboardLayout>
      <ChatWorkspace />
    </DashboardLayout>
  );
}
