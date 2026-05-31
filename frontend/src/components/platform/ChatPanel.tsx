import { Bot, Globe2, Instagram, MessageCircle, MessagesSquare, Send, UserRound, Workflow } from 'lucide-react';
import { useMemo, useState } from 'react';

import { useChat } from '../../hooks/useChat';

const channels = [
  { label: 'WhatsApp', icon: MessageCircle, enabled: false },
  { label: 'Instagram', icon: Instagram, enabled: false },
  { label: 'Messenger', icon: MessagesSquare, enabled: false },
  { label: 'Website Chat', icon: Globe2, enabled: true },
];

const modes = ['IA', 'Humano', 'Hibrido'] as const;

export function ChatPanel() {
  const { conversations, messages, selectedConversationId, setSelectedConversationId, loading, error } = useChat();
  const [mode, setMode] = useState<(typeof modes)[number]>('Hibrido');

  const selectedConversation = useMemo(
    () => conversations.find((conversation) => conversation.id === selectedConversationId) ?? conversations[0] ?? null,
    [conversations, selectedConversationId],
  );

  return (
    <div className="space-y-6">
      <header className="rounded-[1.75rem] border border-white/10 bg-[radial-gradient(circle_at_12%_0%,rgba(34,211,238,0.16),transparent_32%),linear-gradient(145deg,rgba(15,23,42,0.9),rgba(2,6,23,0.76))] p-7">
        <p className="text-xs font-semibold uppercase tracking-[0.25em] text-cyan-200">Omnichannel</p>
        <h1 className="mt-2 font-display text-4xl text-white">Chats</h1>
        <p className="mt-2 max-w-2xl text-sm text-slate-300">
          Central de atendimento para WhatsApp, Instagram, Messenger e Website Chat. Conecte canais reais em Integrations para receber conversas externas.
        </p>
      </header>

      <section className="grid gap-6 xl:grid-cols-[320px_minmax(0,1fr)_340px]">
        <aside className="rounded-3xl border border-white/10 bg-slate-950/60 p-4">
          <h2 className="font-display text-2xl text-white">Conversas</h2>
          <div className="mt-4 grid grid-cols-2 gap-2">
            {channels.map(({ label, icon: Icon, enabled }) => (
              <div key={label} className={`rounded-2xl border p-3 ${enabled ? 'border-cyan-300/30 bg-cyan-300/10 text-cyan-100' : 'border-white/10 bg-white/[0.03] text-slate-400'}`}>
                <Icon size={20} />
                <p className="mt-2 text-xs font-semibold">{label}</p>
                <p className="mt-1 text-[0.68rem]">{enabled ? 'Disponivel' : 'Conectar'}</p>
              </div>
            ))}
          </div>
          <div className="mt-5 space-y-3">
            {loading ? <p className="text-sm text-slate-400">Carregando conversas...</p> : null}
            {!loading && conversations.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-white/15 bg-white/[0.03] p-4 text-sm text-slate-400">
                Nenhuma conversa omnichannel real recebida ainda.
              </div>
            ) : null}
            {conversations.map((conversation) => (
              <button
                key={conversation.id}
                type="button"
                onClick={() => setSelectedConversationId(conversation.id)}
                className={`w-full rounded-2xl border px-4 py-3 text-left transition ${selectedConversationId === conversation.id ? 'border-cyan-300 bg-cyan-300/10 text-white' : 'border-white/10 bg-white/[0.03] text-slate-300 hover:border-white/20'}`}
              >
                <p className="font-semibold">{conversation.title}</p>
                <p className="mt-1 text-xs text-slate-500">Website Chat · {new Date(conversation.created_at).toLocaleString('pt-BR')}</p>
              </button>
            ))}
          </div>
        </aside>

        <main className="flex min-h-[650px] flex-col rounded-3xl border border-white/10 bg-slate-950/55 p-5">
          <div className="flex flex-col gap-3 border-b border-white/10 pb-4 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.22em] text-slate-500">Janela de atendimento</p>
              <h2 className="font-display text-2xl text-white">{selectedConversation?.title ?? 'Sem conversa selecionada'}</h2>
            </div>
            <div className="flex rounded-2xl border border-white/10 bg-black/20 p-1">
              {modes.map((item) => (
                <button
                  key={item}
                  type="button"
                  onClick={() => setMode(item)}
                  className={`rounded-xl px-3 py-2 text-xs font-semibold transition ${mode === item ? 'bg-violet-600 text-white' : 'text-slate-400 hover:text-white'}`}
                >
                  {item}
                </button>
              ))}
            </div>
          </div>

          <div className="flex-1 space-y-4 overflow-y-auto py-5">
            {messages.length === 0 ? (
              <div className="flex h-full items-center justify-center rounded-3xl border border-dashed border-white/15 bg-white/[0.03] p-6 text-center text-slate-400">
                Selecione uma conversa real recebida por canal conectado para atender aqui.
              </div>
            ) : null}
            {messages.map((message) => (
              <article key={message.id} className={`max-w-[78%] rounded-3xl px-5 py-4 ${message.role === 'assistant' ? 'bg-white/10 text-white' : 'ml-auto bg-cyan-100 text-slate-950'}`}>
                <p className="text-xs uppercase tracking-[0.28em] opacity-70">{message.role === 'assistant' ? 'Atendimento' : 'Cliente'}</p>
                <p className="mt-2 whitespace-pre-wrap">{message.text}</p>
              </article>
            ))}
          </div>
          {error ? <p className="text-sm text-coral">{error}</p> : null}
          <div className="flex items-center gap-3 rounded-3xl border border-white/10 bg-white/[0.03] px-4 py-3 text-slate-500">
            <Send size={18} />
            <span className="text-sm">Envio omnichannel sera liberado quando um canal real estiver conectado.</span>
          </div>
        </main>

        <aside className="space-y-6">
          <section className="rounded-3xl border border-white/10 bg-slate-950/60 p-5">
            <div className="flex items-center gap-3">
              <span className="grid h-11 w-11 place-items-center rounded-full bg-cyan-300/12 text-cyan-200">
                <UserRound size={21} />
              </span>
              <div>
                <p className="font-semibold text-white">Painel do cliente</p>
                <p className="text-xs text-slate-400">Dados reais do contato selecionado.</p>
              </div>
            </div>
            <div className="mt-4 rounded-2xl border border-dashed border-white/15 bg-white/[0.03] p-4 text-sm text-slate-400">
              Sem perfil de cliente vinculado a esta conversa.
            </div>
          </section>

          <section className="rounded-3xl border border-white/10 bg-slate-950/60 p-5">
            <div className="flex items-center gap-3">
              <span className="grid h-11 w-11 place-items-center rounded-full bg-violet-500/15 text-violet-200">
                <Workflow size={21} />
              </span>
              <div>
                <p className="font-semibold text-white">Controle IA/Humano</p>
                <p className="text-xs text-slate-400">Modo atual: {mode}</p>
              </div>
            </div>
            <div className="mt-4 rounded-2xl border border-white/10 bg-white/[0.03] p-4 text-sm text-slate-300">
              <div className="flex items-center gap-2">
                <Bot size={18} className="text-violet-200" />
                <span>Sem automacao ativa sem canal conectado.</span>
              </div>
            </div>
          </section>
        </aside>
      </section>
    </div>
  );
}
