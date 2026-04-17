import type { AccountArchivedChatList } from '../../types/account';

interface ArchivedChatsPanelProps {
  data: AccountArchivedChatList | null;
}

export function ArchivedChatsPanel({ data }: ArchivedChatsPanelProps) {
  const items = Array.isArray(data?.items) ? data.items : [];

  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
      <h2 className="font-display text-2xl text-white">Archived Chats / Controls</h2>
      {items.length === 0 ? (
        <p className="mt-3 text-sm text-slate-300">Nenhuma conversa arquivada no momento. Este modulo esta pronto para receber arquivo real no backend.</p>
      ) : (
        <div className="mt-4 space-y-2">
          {items.map((item) => (
            <article key={item.id} className="rounded-2xl border border-white/10 bg-ink/40 px-3 py-2 text-sm text-slate-100">
              {item.title}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
