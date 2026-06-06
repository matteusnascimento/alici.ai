import { ArchiveRestore, MessageSquareDashed } from 'lucide-react';
import { Link } from 'react-router-dom';

import type { AccountArchivedChatList } from '../../types/account';

interface ArchivedChatsPanelProps {
  data: AccountArchivedChatList | null;
}

export function ArchivedChatsPanel({ data }: ArchivedChatsPanelProps) {
  const items = Array.isArray(data?.items) ? data.items : [];

  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
      <div className="mb-5 flex items-center gap-3">
        <ArchiveRestore size={20} className="text-slate-400" />
        <div>
          <h2 className="font-display text-2xl text-white">Conversas Arquivadas</h2>
          <p className="mt-0.5 text-sm text-slate-400">Conversas que você arquivou ficam guardadas aqui.</p>
        </div>
      </div>

      {items.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-white/10 py-16 text-center">
          <MessageSquareDashed size={40} className="mb-4 text-slate-600" />
          <p className="text-base font-semibold text-slate-300">Nenhuma conversa arquivada</p>
          <p className="mt-1 max-w-sm text-sm text-slate-500">
            Quando você arquivar uma conversa, ela aparecerá aqui. Você pode desarquivar a qualquer momento.
          </p>
          <Link
            to="/app/chats"
            className="mt-5 inline-flex items-center gap-2 rounded-xl border border-cyan-400/30 bg-cyan-500/10 px-4 py-2 text-sm font-semibold text-cyan-200 transition hover:bg-cyan-500/20"
          >
            Ir para o chat
          </Link>
        </div>
      ) : (
        <div className="space-y-2">
          {items.map((item) => (
            <article key={item.id} className="rounded-2xl border border-white/10 bg-ink/40 px-4 py-3 text-sm text-slate-100">
              {item.title}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
