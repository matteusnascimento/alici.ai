import { FormEvent, useEffect, useRef, useState } from 'react';

import { useChat } from '../../hooks/useChat';

export function ChatPanel() {
  const { conversations, messages, selectedConversationId, setSelectedConversationId, loading, sending, error, sendMessage } = useChat();
  const [draft, setDraft] = useState('');
  const viewportRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    viewportRef.current?.scrollTo({ top: viewportRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!draft.trim()) {
      return;
    }
    const text = draft;
    setDraft('');
    try {
      await sendMessage(text);
    } catch {
      setDraft(text);
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[320px_1fr]">
      <aside className="panel-base">
        <div className="flex items-center justify-between">
          <h3 className="font-display text-2xl text-white">Conversas</h3>
          <button className="rounded-full border border-white/10 px-4 py-2 text-sm text-white transition hover:border-cyan" onClick={() => setSelectedConversationId(null)} type="button">
            Nova
          </button>
        </div>
        <div className="mt-6 space-y-3">
          {loading ? <p className="text-slate-300">Carregando conversas...</p> : null}
          {!loading && conversations.length === 0 ? <p className="text-slate-300">Nenhuma conversa ainda.</p> : null}
          {conversations.map((conversation) => (
            <button
              key={conversation.id}
              className={`w-full rounded-2xl border px-4 py-3 text-left transition ${selectedConversationId === conversation.id ? 'border-cyan bg-white/10 text-white' : 'border-white/10 bg-white/5 text-slate-200 hover:border-white/20'}`}
              onClick={() => setSelectedConversationId(conversation.id)}
              type="button"
            >
              <p className="font-medium">{conversation.title}</p>
              <p className="mt-1 text-xs text-slate-400">{new Date(conversation.created_at).toLocaleString('pt-BR')}</p>
            </button>
          ))}
        </div>
      </aside>
      <section className="panel-base flex min-h-[620px] flex-col">
        <div ref={viewportRef} className="flex-1 space-y-4 overflow-y-auto pr-2">
          {messages.length === 0 ? (
            <div className="flex h-full items-center justify-center rounded-3xl border border-dashed border-white/10 bg-white/5 text-center text-slate-300">
              Envie a primeira mensagem para abrir a conversa com a Alici.
            </div>
          ) : null}
          {messages.map((message) => (
            <article key={message.id} className={`max-w-[80%] rounded-3xl px-5 py-4 ${message.role === 'assistant' ? 'bg-white/10 text-white' : 'ml-auto bg-sand text-ink'}`}>
              <p className="text-xs uppercase tracking-[0.3em] opacity-70">{message.role === 'assistant' ? 'Alici' : 'Você'}</p>
              <p className="mt-2 whitespace-pre-wrap">{message.text}</p>
            </article>
          ))}
        </div>
        {error ? <p className="mt-4 text-sm text-coral">{error}</p> : null}
        <form className="mt-6 flex flex-col gap-4 lg:flex-row" onSubmit={handleSubmit}>
          <textarea
            className="min-h-28 flex-1 rounded-3xl border border-white/10 bg-white/5 px-5 py-4 text-white outline-none focus:border-cyan"
            placeholder="Descreva sua necessidade, campanha ou tarefa operacional..."
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
          />
          <button className="rounded-3xl bg-sand px-6 py-4 font-semibold text-ink transition hover:bg-white disabled:opacity-60" disabled={sending} type="submit">
            {sending ? 'Enviando...' : 'Enviar'}
          </button>
        </form>
      </section>
    </div>
  );
}
