import { FormEvent, useEffect, useMemo, useRef, useState } from 'react';
import {
  Bell,
  Bot,
  Building2,
  CircleHelp,
  DatabaseZap,
  LineChart,
  Loader2,
  Megaphone,
  MessageSquarePlus,
  Search,
  Send,
  Settings,
  Sparkles,
  TrendingUp,
} from 'lucide-react';

import { useChat } from '../../hooks/useChat';
import { getChatChannels } from '../../services/chats.service';
import { getRevenueIntelligence } from '../../services/revenue.service';
import type { ChatChannel } from '../../types/chats';
import type { RevenueIntelligenceSnapshot } from '../../services/revenue.service';

const suggestionCards = [
  { label: 'Como foi nosso faturamento neste mes?', icon: LineChart },
  { label: 'Quais canais estao trazendo mais reservas?', icon: DatabaseZap },
  { label: 'Me mostre o desempenho das campanhas', icon: Megaphone },
  { label: 'Quais sao os principais insights do Business Pulse?', icon: Sparkles },
  { label: 'Gere um plano de acao para o proximo mes', icon: TrendingUp },
];

function formatCurrency(value: number) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(value);
}

export function AxiAssistantPage() {
  const { conversations, messages, selectedConversationId, setSelectedConversationId, loading, sending, error, sendMessage } = useChat();
  const [draft, setDraft] = useState('');
  const [channels, setChannels] = useState<ChatChannel[]>([]);
  const [revenue, setRevenue] = useState<RevenueIntelligenceSnapshot | null>(null);
  const viewportRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    void Promise.all([getChatChannels(), getRevenueIntelligence(30)])
      .then(([channelData, revenueData]) => {
        setChannels(channelData);
        setRevenue(revenueData);
      })
      .catch(() => {
        setChannels([]);
        setRevenue(null);
      });
  }, []);

  useEffect(() => {
    const viewport = viewportRef.current;
    if (!viewport || typeof viewport.scrollTo !== 'function') {
      return;
    }
    viewport.scrollTo({ top: viewport.scrollHeight, behavior: 'smooth' });
  }, [messages]);

  const insightItems = useMemo(() => {
    if (!revenue) return [];
    const items = [];
    if (revenue.receita_por_canal[0]) {
      items.push(`${revenue.receita_por_canal[0].label} lidera receita no periodo.`);
    }
    if (revenue.summary.conversao_total > 0) {
      items.push(`Conversao atual: ${revenue.summary.conversao_total.toFixed(1)}%.`);
    }
    if (revenue.summary.reservas_fechadas > 0) {
      items.push(`${revenue.summary.reservas_fechadas} reservas fechadas nos ultimos 30 dias.`);
    }
    return items;
  }, [revenue]);

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
    <div className="min-h-[calc(100vh-2rem)] rounded-[1.75rem] bg-[#f7f8ff] p-5 text-slate-950 shadow-[0_24px_90px_rgba(15,23,42,0.18)]">
      <header className="mb-5 flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
        <div className="flex items-center gap-4">
          <span className="grid h-12 w-12 place-items-center rounded-2xl bg-violet-600 text-white shadow-[0_14px_38px_rgba(124,58,237,0.28)]">
            <Bot size={25} />
          </span>
          <div>
            <h1 className="font-display text-3xl text-slate-950">AXI Assistant</h1>
            <p className="mt-1 text-sm text-slate-600">Seu assistente inteligente para analisar, planejar e crescer.</p>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <label className="flex min-w-[320px] items-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-500 shadow-sm">
            <Search size={18} />
            <span>Buscar no Assistente...</span>
            <span className="ml-auto text-xs text-slate-400">⌘ K</span>
          </label>
          <button
            type="button"
            onClick={() => setSelectedConversationId(null)}
            className="inline-flex items-center gap-2 rounded-xl border border-violet-500 bg-white px-5 py-3 text-sm font-semibold text-violet-700 shadow-sm"
          >
            <MessageSquarePlus size={17} />
            Nova conversa
          </button>
          <Bell size={22} className="text-slate-900" />
          <CircleHelp size={22} className="text-slate-900" />
          <Settings size={22} className="text-slate-900" />
        </div>
      </header>

      <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_360px]">
        <main className="space-y-5">
          <section className="relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
            <div className="absolute right-16 top-8 hidden h-32 w-32 rounded-full bg-violet-100 blur-2xl md:block" />
            <div className="relative max-w-2xl">
              <p className="text-2xl font-bold text-slate-950">Ola, Mateus!</p>
              <h2 className="mt-2 font-display text-4xl text-violet-700">Como posso te ajudar hoje?</h2>
              <p className="mt-4 max-w-xl text-sm leading-6 text-slate-600">
                Consulte dados, gere analises, obtenha insights e receba recomendacoes para o crescimento do seu negocio.
              </p>
            </div>
          </section>

          <section>
            <h2 className="mb-3 text-lg font-bold text-slate-950">Sugestoes para voce</h2>
            <div className="grid gap-3 md:grid-cols-3 xl:grid-cols-5">
              {suggestionCards.map(({ label, icon: Icon }) => (
                <button
                  key={label}
                  type="button"
                  onClick={() => setDraft(label)}
                  className="rounded-2xl border border-slate-200 bg-white p-4 text-center text-sm font-semibold text-slate-900 shadow-sm transition hover:border-violet-300 hover:text-violet-700"
                >
                  <Icon className="mx-auto mb-3 text-violet-600" size={30} />
                  {label}
                </button>
              ))}
            </div>
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <h2 className="mb-4 text-lg font-bold text-slate-950">Converse com o AXI</h2>
            <div ref={viewportRef} className="max-h-[520px] min-h-[360px] space-y-4 overflow-y-auto pr-2">
              {loading ? <Loader2 className="mx-auto mt-20 animate-spin text-violet-600" /> : null}
              {!loading && messages.length === 0 ? (
                <div className="grid min-h-72 place-items-center rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-6 text-center text-sm text-slate-500">
                  Nenhuma consulta interna ainda. Pergunte sobre Revenue, Marketing, reservas ou operacao.
                </div>
              ) : null}
              {messages.map((message) => (
                <article
                  key={message.id}
                  className={[
                    'max-w-[82%] rounded-2xl px-5 py-4 text-sm shadow-sm',
                    message.role === 'assistant'
                      ? 'border border-slate-200 bg-white text-slate-900'
                      : 'ml-auto bg-violet-100 text-slate-950',
                  ].join(' ')}
                >
                  <p className="mb-2 text-xs font-semibold text-violet-700">{message.role === 'assistant' ? 'AXI Assistant' : 'Voce'}</p>
                  <p className="whitespace-pre-wrap leading-6">{message.text}</p>
                </article>
              ))}
            </div>
            {error ? <p className="mt-3 text-sm text-rose-600">{error}</p> : null}
            <form onSubmit={handleSubmit} className="mt-5 flex items-center gap-3 rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-sm">
              <input
                className="min-w-0 flex-1 bg-transparent text-sm text-slate-950 outline-none placeholder:text-slate-400"
                placeholder="Pergunte sobre dados, relatorios, campanhas ou plano de acao..."
                value={draft}
                onChange={(event) => setDraft(event.target.value)}
              />
              <button aria-label="Enviar" className="grid h-12 w-12 place-items-center rounded-xl bg-violet-600 text-white disabled:opacity-50" disabled={sending || !draft.trim()} type="submit">
                <Send size={20} />
              </button>
            </form>
          </section>
        </main>

        <aside className="space-y-4">
          <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="font-bold text-slate-950">Fontes de dados</h2>
              <span className="text-xs font-semibold text-violet-700">Ver todas</span>
            </div>
            <div className="space-y-3">
              {channels.length === 0 ? (
                <p className="rounded-xl bg-slate-50 p-4 text-sm text-slate-500">Nenhum canal configurado ainda.</p>
              ) : channels.map((channel) => (
                <div key={channel.key} className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-3 font-semibold text-slate-800">
                    <span className="grid h-7 w-7 place-items-center rounded-lg bg-violet-100 text-violet-700">
                      <Building2 size={15} />
                    </span>
                    {channel.label}
                  </span>
                  <span className={channel.status === 'connected' ? 'text-emerald-600' : 'text-amber-600'}>
                    {channel.status === 'connected' ? 'Sincronizado' : 'Nao configurado'}
                  </span>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="font-bold text-slate-950">Business Pulse</h2>
              <span className="text-xs font-semibold text-violet-700">Ver dashboard</span>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">
                <p className="text-xs text-slate-500">Receita</p>
                <p className="mt-2 text-xl font-bold">{formatCurrency(revenue?.summary.receita_total ?? 0)}</p>
              </div>
              <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">
                <p className="text-xs text-slate-500">Reservas</p>
                <p className="mt-2 text-xl font-bold">{revenue?.summary.reservas_fechadas ?? 0}</p>
              </div>
              <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">
                <p className="text-xs text-slate-500">Conversao</p>
                <p className="mt-2 text-xl font-bold">{(revenue?.summary.conversao_total ?? 0).toFixed(1)}%</p>
              </div>
              <div className="rounded-xl border border-slate-100 bg-slate-50 p-4">
                <p className="text-xs text-slate-500">Ticket medio</p>
                <p className="mt-2 text-xl font-bold">{formatCurrency(revenue?.summary.ticket_medio ?? 0)}</p>
              </div>
            </div>
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="font-bold text-slate-950">Insights recentes</h2>
              <span className="text-xs font-semibold text-violet-700">Ver todos</span>
            </div>
            {insightItems.length === 0 ? (
              <p className="rounded-xl bg-slate-50 p-4 text-sm text-slate-500">Sem dados suficientes para gerar insights sem simular resultados.</p>
            ) : (
              <div className="space-y-3">
                {insightItems.map((item) => (
                  <div key={item} className="flex gap-3 rounded-xl bg-slate-50 p-3 text-sm text-slate-700">
                    <Sparkles size={17} className="mt-0.5 text-violet-600" />
                    <p>{item}</p>
                  </div>
                ))}
              </div>
            )}
          </section>
        </aside>
      </div>
    </div>
  );
}
