import type { AgentKnowledgeSource } from '../../../types/agentsV2';

interface AgentKnowledgeLibraryProps {
  items: AgentKnowledgeSource[];
}

export function AgentKnowledgeLibrary({ items }: AgentKnowledgeLibraryProps) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <p className="font-semibold text-white">Materiais e informacoes do agente</p>
      <div className="mt-3 space-y-2">
        {items.map((item) => (
          <div key={item.id} className="rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm text-slate-200">
            <p>{item.title || item.materiais_e_informacoes_do_agente}</p>
            <p className="text-xs text-slate-400">{item.kind || item.tipo}</p>
          </div>
        ))}
        {items.length === 0 ? <p className="text-xs text-slate-400">Sem materiais cadastrados.</p> : null}
      </div>
    </div>
  );
}
