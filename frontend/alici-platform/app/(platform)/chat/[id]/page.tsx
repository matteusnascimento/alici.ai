import { DashboardLayout } from "@/layouts/DashboardLayout";
import { ChatWorkspace } from "@/components/chat/ChatWorkspace";

interface ChatDetailRouteProps {
  params: { id: string };
}

export default function ChatDetailRoute({ params }: ChatDetailRouteProps) {
  return (
    <DashboardLayout>
      <ChatWorkspace initialConversationId={params.id} />
    </DashboardLayout>
  );
}
