import { DashboardLayout } from "@/layouts/DashboardLayout";

interface ChatDetailRouteProps {
  params: { id: string };
}

export default function ChatDetailRoute({ params }: ChatDetailRouteProps) {
  return (
    <DashboardLayout>
      <main className="space-y-4 p-2">
        <h1 className="text-2xl font-semibold">Conversation {params.id}</h1>
        <p className="text-sm text-slate-300">Rota dedicada para abertura de conversa por ID.</p>
      </main>
    </DashboardLayout>
  );
}
