
interface AgentDetailRouteProps {
  params: { id: string };
}

export default function AgentDetailRoute({ params }: AgentDetailRouteProps) {
  return (
      <main className="space-y-4 p-2">
        <h1 className="text-2xl font-semibold">Agent {params.id}</h1>
        <p className="text-sm text-slate-300">Detalhe de agente com rota ativa para `GET /api/agents/{'{id}'}`.</p>
      </main>
  );
}
