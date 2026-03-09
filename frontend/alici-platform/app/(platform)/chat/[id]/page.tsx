import { ChatWorkspace } from "@/components/chat/ChatWorkspace";

interface ChatDetailRouteProps {
  params: { id: string };
}

export default function ChatDetailRoute({ params }: ChatDetailRouteProps) {
  return (
      <ChatWorkspace initialConversationId={params.id} />
  );
}
