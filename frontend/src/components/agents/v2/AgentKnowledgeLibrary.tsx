import type { AgentKnowledgeSource } from '../../../types/agentsV2';

interface AgentKnowledgeLibraryProps {
  items: AgentKnowledgeSource[];
  deletingId?: number | null;
  onDelete: (sourceId: number) => Promise<void>;
}

function formatKind(kind: string) {
  if (kind.startsWith('file:')) {
    return `Arquivo ${kind.replace('file:', '').toUpperCase()}`;
  }
  if (kind === 'manual') return 'Conteudo manual';
  if (kind === 'faq') return 'FAQ';
  return kind;
}

export function AgentKnowledgeLibrary({ items, deletingId = null, onDelete }: AgentKnowledgeLibraryProps) {
  const safeItems = Array.isArray(items) ? items : [];

  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.04] p-5 shadow-soft">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="font-display text-lg text-white">Biblioteca do agente</h2>
          <p className="mt-1 text-sm text-slate-300">Materiais cadastrados para respostas e contexto da IA.</p>
        </div>
        <span className="rounded-full border border-white/15 bg-white/[0.04] px-3 py-1 text-xs text-slate-300">{safeItems.length} itens</span>
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-2">
        {safeItems.map((item) => (
          <article key={item.id} className="rounded-2xl border border-white/10 bg-gradient-to-b from-black/30 to-black/15 p-4">
            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-white">{item.title}</p>
                <p className="mt-1 text-xs text-cyan-200">{formatKind(item.kind)}</p>
              </div>
              <button
                type="button"
                onClick={() => void onDelete(item.id)}
                disabled={deletingId === item.id}
                className="rounded-lg border border-white/15 px-2 py-1 text-xs text-slate-300 transition hover:border-rose-300/50 hover:text-rose-200 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {deletingId === item.id ? 'Removendo...' : 'Remover'}
              </button>
            </div>

            {item.content ? <p className="mt-3 line-clamp-3 text-xs text-slate-400">{item.content}</p> : null}

            <div className="mt-3 flex items-center justify-between text-[11px] text-slate-500">
              <span>{item.enabled === false ? 'Inativo' : 'Ativo'}</span>
              <span>{item.updated_at ? new Date(item.updated_at).toLocaleDateString('pt-BR') : ''}</span>
            </div>
          </article>
        ))}
        {safeItems.length === 0 ? (
          <p className="rounded-xl border border-white/10 bg-black/20 px-3 py-4 text-sm text-slate-400">Sem materiais cadastrados.</p>
        ) : null}
      </div>
    </section>
  );
}
