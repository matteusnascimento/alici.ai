import { useParams } from 'react-router-dom';

import { useAgentKnowledge } from '../../../hooks/agentsV2/useAgentKnowledge';
import { AgentFaqManager } from './AgentFaqManager';
import { AgentKnowledgeLibrary } from './AgentKnowledgeLibrary';
import { AgentKnowledgeUpload } from './AgentKnowledgeUpload';

export function AgentKnowledgePage() {
  const params = useParams();
  const agentId = Number(params.id || 0);
  const { data, loading, error, add } = useAgentKnowledge(agentId);

  if (loading) return <p className="text-slate-300">Carregando materiais...</p>;
  if (error) return <p className="text-red-300">{error}</p>;

  return (
    <div className="space-y-4">
      <header className="rounded-3xl border border-white/10 bg-white/5 p-4">
        <h1 className="font-display text-2xl text-white">Materiais e informacoes do agente</h1>
      </header>
      <div className="grid gap-3 lg:grid-cols-2">
        <AgentKnowledgeUpload onAdd={(payload) => void add(payload)} />
        <AgentFaqManager onAddFaq={(question, answer) => void add({ title: question, kind: 'faq', content: answer })} />
      </div>
      <AgentKnowledgeLibrary items={data} />
    </div>
  );
}
