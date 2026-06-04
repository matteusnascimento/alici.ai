import { KeyboardEvent, useMemo, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { ChevronRight, Loader2, Send, Sparkles } from 'lucide-react';

import { useChat } from '../../hooks/useChat';

type MiniAssistantContext = 'revenue' | 'marketing' | 'studio' | 'chats';

const quickActions = [
  'Criar campanha',
  'Criar post',
  'Criar planilha',
  'Criar apresentacao',
  'Criar anuncio',
  'Criar plano de acao',
  'Analisar Revenue',
  'Gerar relatorio',
];

const contextCopy: Record<MiniAssistantContext, string> = {
  revenue: 'revenue, reservas, leads, forecast, conversoes',
  marketing: 'campanhas, calendario, conteudo, audiencias, ROI',
  studio: 'design, criativos, posts, videos, templates',
  chats: 'mensagens, clientes, atendimento, tags, historico e controle IA humano',
};

export function MiniAssistantCard({ context }: { context: MiniAssistantContext }) {
  const { messages, loading, sending, error, sendMessage } = useChat();
  const [draft, setDraft] = useState('');
  const inputRef = useRef<HTMLInputElement | null>(null);
  const assistantContext = contextCopy[context];

  const visibleMessages = useMemo(() => messages.slice(-3), [messages]);

  async function submitMessage() {
    const text = draft.trim();
    if (!text) return;
    setDraft('');
    try {
      await sendMessage(text, assistantContext);
    } catch {
      setDraft(text);
    }
  }

  function handleInputKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key !== 'Enter') return;
    event.preventDefault();
    void submitMessage();
  }

  function applyQuickAction(action: string) {
    setDraft(action);
    inputRef.current?.focus();
  }

  return (
    <section className="rounded-2xl border border-violet-300/20 bg-[radial-gradient(circle_at_16%_0%,rgba(168,85,247,0.26),transparent_40%),linear-gradient(155deg,rgba(15,23,42,0.96),rgba(2,6,23,0.82))] p-5 text-white shadow-[0_22px_70px_rgba(76,29,149,0.24)]">
      <div className="flex items-start gap-3">
        <span className="mt-0.5 grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-violet-500/18 text-violet-100">
          <Sparkles size={19} />
        </span>
        <div>
          <h2 className="font-display text-xl text-white">AXI Assistant</h2>
          <p className="mt-1 text-sm leading-5 text-slate-300">Seu assistente executivo de IA para criar, analisar e executar.</p>
        </div>
      </div>

      <p className="mt-5 text-sm font-semibold text-violet-100">O que deseja fazer hoje?</p>
      <div className="mt-3 flex flex-wrap gap-2">
        {quickActions.map((action) => (
          <button
            key={action}
            type="button"
            onClick={() => applyQuickAction(action)}
            className="rounded-full border border-white/10 bg-white/[0.045] px-3 py-2 text-xs font-semibold text-slate-200 transition hover:border-violet-300/45 hover:bg-white/[0.08] hover:text-white"
          >
            {action}
          </button>
        ))}
      </div>

      <div className="mt-5 rounded-2xl border border-white/10 bg-slate-950/48 p-3">
        <p className="mb-3 text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">Ultima conversa</p>
        {loading ? (
          <div className="grid min-h-28 place-items-center">
            <Loader2 size={18} className="animate-spin text-violet-300" />
          </div>
        ) : visibleMessages.length ? (
          <div className="max-h-60 space-y-3 overflow-y-auto pr-1">
            {visibleMessages.map((message) => (
              <article key={message.id} className="rounded-xl border border-white/10 bg-white/[0.035] px-3 py-2 text-sm">
                <p className="text-xs font-semibold text-violet-200">{message.role === 'assistant' ? 'AXI' : 'Voce'}:</p>
                <p className="mt-1 whitespace-pre-wrap leading-5 text-slate-200">{message.text}</p>
              </article>
            ))}
          </div>
        ) : (
          <div className="grid min-h-28 place-items-center rounded-xl border border-dashed border-white/10 bg-white/[0.025] p-3 text-center text-sm text-slate-400">
            Inicie uma conversa com o AXI Assistant.
          </div>
        )}
      </div>

      {error ? <p className="mt-3 rounded-xl border border-rose-400/25 bg-rose-500/10 px-3 py-2 text-sm text-rose-100">{error}</p> : null}

      <div className="mt-4 flex items-center gap-2 rounded-2xl border border-white/10 bg-slate-950/70 px-3 py-2">
        <input
          ref={inputRef}
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={handleInputKeyDown}
          className="min-w-0 flex-1 bg-transparent text-sm text-white outline-none placeholder:text-slate-500"
          placeholder="Digite sua solicitacao..."
        />
        <button
          aria-label="Enviar ao AXI Assistant"
          disabled={sending || !draft.trim()}
          onClick={() => void submitMessage()}
          type="button"
          className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-violet-600 text-white transition hover:bg-violet-500 disabled:opacity-50"
        >
          {sending ? <Loader2 size={17} className="animate-spin" /> : <Send size={17} />}
        </button>
      </div>

      <Link to="/app/assistant" className="mt-4 flex items-center justify-between rounded-xl border border-violet-300/30 bg-white/[0.035] px-4 py-3 text-sm font-semibold text-violet-100 transition hover:border-violet-200/60 hover:bg-white/[0.07]">
        Abrir AXI Assistant
        <ChevronRight size={17} />
      </Link>
    </section>
  );
}
