import {
  Bot,
  CalendarDays,
  ChevronDown,
  ChevronRight,
  CircleDollarSign,
  Clock,
  FileText,
  Image,
  Inbox,
  Link2,
  Loader2,
  MessageCircle,
  MoreVertical,
  Paperclip,
  Search,
  Send,
  Smile,
  Sparkles,
  Star,
  Tag,
  UserPlus,
  Users,
  Zap,
} from 'lucide-react';
import { FormEvent, useEffect, useMemo, useState } from 'react';

import { ApiError } from '../../services/api';
import {
  getAiSuggestions,
  getChatChannels,
  getChatSummary,
  getChatTags,
  getChatTeam,
  getCustomerReservations,
  getOmnichannelConversation,
  getOmnichannelConversations,
  sendOmnichannelMessage,
  updateConversationAiMode,
} from '../../services/chats.service';
import type {
  ChatChannel,
  ChatSummary,
  ChatTag,
  ChatTeamMember,
  ConversationDetail,
  CustomerReservation,
  OmnichannelConversation,
  OmnichannelMessage,
} from '../../types/chats';

const channelColors: Record<string, string> = {
  whatsapp: 'bg-emerald-500 text-white',
  instagram: 'bg-pink-500 text-white',
  messenger: 'bg-blue-500 text-white',
  website_chat: 'bg-sky-500 text-white',
};

const filters = [
  { key: 'all', label: 'Todas as conversas' },
  { key: 'unassigned', label: 'Nao atribuidas' },
  { key: 'mine', label: 'Minhas conversas' },
  { key: 'ai', label: 'Com IA' },
  { key: 'human', label: 'Aguardando humano' },
  { key: 'closed', label: 'Finalizadas' },
] as const;

function timeLabel(value?: string | null) {
  if (!value) return '--:--';
  return new Date(value).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

function dateLabel(value?: string | null) {
  if (!value) return 'Sem data';
  return new Date(value).toLocaleDateString('pt-BR');
}

function money(value: number) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
}

function ChannelIcon({ channel }: { channel: string }) {
  return (
    <span className={`grid h-7 w-7 place-items-center rounded-full ${channelColors[channel] ?? 'bg-slate-600 text-white'}`}>
      <MessageCircle size={15} />
    </span>
  );
}

function SectionTitle({ children }: { children: string }) {
  return <p className="px-3 text-xs uppercase tracking-[0.18em] text-slate-500">{children}</p>;
}

function EmptyPanel({ children }: { children: string }) {
  return (
    <div className="grid min-h-40 place-items-center rounded-lg border border-dashed border-white/10 bg-white/[0.03] p-6 text-center text-sm text-slate-400">
      {children}
    </div>
  );
}

function MessageBubble({ message }: { message: OmnichannelMessage }) {
  const outgoing = message.sender_type === 'assistant' || message.sender_type === 'human';
  return (
    <article className={`max-w-[78%] rounded-lg border px-4 py-3 text-sm shadow-soft ${outgoing ? 'ml-auto border-violet-400/30 bg-violet-700/70 text-white' : 'border-white/10 bg-slate-900/90 text-slate-100'}`}>
      <div className="mb-2 flex items-center justify-between gap-3 text-xs text-slate-300">
        <span>{message.sender_type === 'assistant' ? 'IA respondeu' : message.sender_type === 'human' ? 'Atendente' : 'Cliente'}</span>
        <span>{timeLabel(message.created_at)}</span>
      </div>
      <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
      <p className="mt-2 text-[11px] text-slate-400">{message.message_type} · {message.delivery_status} · {message.channel}</p>
    </article>
  );
}

export function ChatsPage() {
  const [summary, setSummary] = useState<ChatSummary | null>(null);
  const [channels, setChannels] = useState<ChatChannel[]>([]);
  const [team, setTeam] = useState<ChatTeamMember[]>([]);
  const [tags, setTags] = useState<ChatTag[]>([]);
  const [conversations, setConversations] = useState<OmnichannelConversation[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [detail, setDetail] = useState<ConversationDetail | null>(null);
  const [reservations, setReservations] = useState<CustomerReservation[]>([]);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [activeChannel, setActiveChannel] = useState<string>('all');
  const [activeFilter, setActiveFilter] = useState<(typeof filters)[number]['key']>('all');
  const [mode, setMode] = useState<'ia' | 'humano' | 'hibrido'>('hibrido');
  const [draft, setDraft] = useState('');
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sendError, setSendError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        setLoading(true);
        const [summaryData, channelData, teamData, tagData, conversationData] = await Promise.all([
          getChatSummary(),
          getChatChannels(),
          getChatTeam(),
          getChatTags(),
          getOmnichannelConversations(),
        ]);
        if (!cancelled) {
          setSummary(summaryData);
          setChannels(channelData);
          setTeam(teamData);
          setTags(tagData);
          setConversations(conversationData);
          setSelectedId(conversationData[0]?.id ?? null);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Falha ao carregar Chats');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function loadDetail() {
      if (!selectedId) {
        setDetail(null);
        setReservations([]);
        return;
      }
      try {
        setDetailLoading(true);
        const data = await getOmnichannelConversation(selectedId);
        const reservationData = await getCustomerReservations(data.conversation.customer_id);
        if (!cancelled) {
          setDetail(data);
          setReservations(reservationData.items);
          setMode(data.conversation.ai_mode);
          setSuggestions([]);
          setSendError(null);
        }
      } catch (err) {
        if (!cancelled) setSendError(err instanceof Error ? err.message : 'Falha ao abrir conversa');
      } finally {
        if (!cancelled) setDetailLoading(false);
      }
    }
    void loadDetail();
    return () => {
      cancelled = true;
    };
  }, [selectedId]);

  const filteredConversations = useMemo(() => {
    return conversations.filter((conversation) => {
      if (activeChannel !== 'all' && conversation.channel !== activeChannel) return false;
      if (activeFilter === 'unassigned') return !conversation.assigned_to;
      if (activeFilter === 'ai') return conversation.ai_mode === 'ia';
      if (activeFilter === 'human') return conversation.status === 'awaiting_human' || conversation.ai_mode === 'humano';
      if (activeFilter === 'closed') return conversation.status === 'closed';
      return true;
    });
  }, [activeChannel, activeFilter, conversations]);

  const filterCounts = useMemo(() => {
    return {
      all: conversations.length,
      unassigned: conversations.filter((item) => !item.assigned_to).length,
      mine: conversations.filter((item) => item.assigned_to).length,
      ai: conversations.filter((item) => item.ai_mode === 'ia').length,
      human: conversations.filter((item) => item.status === 'awaiting_human' || item.ai_mode === 'humano').length,
      closed: conversations.filter((item) => item.status === 'closed').length,
    };
  }, [conversations]);

  const currentConversation = detail?.conversation ?? conversations.find((item) => item.id === selectedId) ?? null;
  const totalSpent = reservations.reduce((sum, item) => sum + item.value, 0);

  async function handleModeChange(nextMode: 'ia' | 'humano' | 'hibrido') {
    setMode(nextMode);
    if (!currentConversation) return;
    try {
      const updated = await updateConversationAiMode(currentConversation.id, nextMode);
      setConversations((items) => items.map((item) => (item.id === updated.id ? { ...item, ...updated } : item)));
      setDetail((current) => current ? { ...current, conversation: { ...current.conversation, ...updated } } : current);
    } catch (err) {
      setSendError(err instanceof Error ? err.message : 'Falha ao atualizar modo');
    }
  }

  async function handleSuggestions() {
    if (!currentConversation) return;
    try {
      const response = await getAiSuggestions(currentConversation.id);
      setSuggestions(response.items);
      setSendError(null);
    } catch (err) {
      setSendError(err instanceof Error ? err.message : 'Provider de IA indisponivel para sugestoes.');
    }
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!currentConversation || !draft.trim()) return;
    try {
      await sendOmnichannelMessage(currentConversation.id, draft.trim());
      setDraft('');
      setSendError(null);
      const data = await getOmnichannelConversation(currentConversation.id);
      setDetail(data);
    } catch (err) {
      if (err instanceof ApiError) {
        setSendError(err.message);
      } else {
        setSendError(err instanceof Error ? err.message : 'Mensagem nao enviada');
      }
    }
  }

  if (loading) {
    return (
      <div className="grid min-h-[70vh] place-items-center">
        <Loader2 className="animate-spin text-cyan" size={28} />
      </div>
    );
  }

  if (error) {
    return <div className="rounded-lg border border-rose-500/30 bg-rose-500/10 p-5 text-rose-100">{error}</div>;
  }

  return (
    <div className="min-h-[calc(100vh-2rem)] rounded-xl border border-white/10 bg-[#050914] p-4 text-white shadow-[0_24px_90px_rgba(0,0,0,0.45)]">
      <header className="mb-4 flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
        <div>
          <h1 className="font-display text-3xl">Chats</h1>
          <p className="mt-1 text-sm text-slate-400">Central de atendimento omnichannel</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <div className="flex items-center gap-3 rounded-lg border border-white/10 bg-slate-950/70 px-4 py-3">
            <span className={`h-2.5 w-2.5 rounded-full ${summary?.provider_status === 'connected' ? 'bg-emerald-400' : 'bg-amber-400'}`} />
            <div>
              <p className="text-sm font-semibold">{summary?.provider_status === 'connected' ? 'IA ativa' : 'IA nao configurada'}</p>
              <p className="text-xs text-slate-400">Sugestoes usam provider real</p>
            </div>
          </div>
          <label className="flex items-center gap-2 rounded-lg border border-violet-400/30 bg-violet-500/10 px-4 py-3 text-sm">
            <Sparkles size={16} />
            <select className="bg-transparent font-semibold outline-none" value={mode} onChange={(event) => void handleModeChange(event.target.value as typeof mode)}>
              <option className="bg-slate-950" value="ia">Modo IA</option>
              <option className="bg-slate-950" value="hibrido">Modo hibrido</option>
              <option className="bg-slate-950" value="humano">Modo humano</option>
            </select>
          </label>
          <label className="flex min-w-[260px] items-center gap-3 rounded-lg border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-slate-400">
            <Search size={17} />
            <span>Buscar conversas...</span>
          </label>
        </div>
      </header>

      <div className="grid gap-3 xl:grid-cols-[240px_330px_minmax(420px,1fr)_320px]">
        <aside className="space-y-5 rounded-lg border border-white/10 bg-slate-950/55 p-3">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <SectionTitle>Canais</SectionTitle>
              <button type="button" className="grid h-7 w-7 place-items-center rounded-lg border border-white/10 text-slate-300">+</button>
            </div>
            {channels.map((channel) => (
              <button
                key={channel.key}
                type="button"
                onClick={() => setActiveChannel(channel.key)}
                className={`flex w-full items-center gap-3 rounded-lg border px-3 py-3 text-left text-sm transition ${activeChannel === channel.key ? 'border-violet-400/50 bg-violet-600/35 text-white' : 'border-transparent bg-white/[0.03] text-slate-300 hover:border-white/10'}`}
              >
                <ChannelIcon channel={channel.key} />
                <span className="flex-1">{channel.label}</span>
                <span className="rounded-lg bg-white/10 px-2 py-1 text-xs">{channel.open_count}</span>
              </button>
            ))}
          </div>

          <div className="space-y-2">
            <SectionTitle>Filtros</SectionTitle>
            {filters.map((filter) => (
              <button
                key={filter.key}
                type="button"
                onClick={() => setActiveFilter(filter.key)}
                className={`flex w-full items-center gap-2 rounded-lg border px-3 py-2 text-left text-sm transition ${activeFilter === filter.key ? 'border-violet-400/50 bg-violet-600/30 text-white' : 'border-transparent text-slate-300 hover:bg-white/[0.04]'}`}
              >
                <Inbox size={14} />
                <span className="flex-1">{filter.label}</span>
                <span className="rounded-md bg-white/10 px-2 py-0.5 text-xs">{filterCounts[filter.key]}</span>
              </button>
            ))}
          </div>

          <div className="space-y-2">
            <SectionTitle>Equipes</SectionTitle>
            <div className="flex items-center gap-2 rounded-lg border border-violet-400/40 bg-violet-600/25 px-3 py-2 text-sm">
              <Users size={14} />
              <span className="flex-1">Todos os atendentes</span>
              <span className="rounded-md bg-white/10 px-2 py-0.5 text-xs">{conversations.length}</span>
            </div>
            {team.map((member) => (
              <div key={member.id} className="flex items-center gap-2 px-3 py-1.5 text-sm text-slate-300">
                <span className={`h-2.5 w-2.5 rounded-full ${member.status === 'online' ? 'bg-emerald-400' : 'bg-slate-500'}`} />
                <span className="flex-1 truncate">{member.name}</span>
                <span className="rounded-md bg-white/10 px-2 py-0.5 text-xs">{member.assigned_count}</span>
              </div>
            ))}
          </div>

          <div className="space-y-2">
            <SectionTitle>Tags</SectionTitle>
            {tags.map((tag) => (
              <div key={tag.id} className="flex items-center gap-2 px-3 py-1.5 text-sm text-slate-300">
                <span className="h-2.5 w-2.5 rounded-full bg-violet-400" />
                {tag.label}
              </div>
            ))}
          </div>
        </aside>

        <aside className="rounded-lg border border-white/10 bg-slate-950/55">
          <div className="flex items-center justify-between border-b border-white/10 p-4">
            <h2 className="font-display text-xl">Conversas</h2>
            <button type="button" className="flex items-center gap-1 text-xs text-slate-400">Mais recentes <ChevronDown size={14} /></button>
          </div>
          <div className="max-h-[calc(100vh-190px)] overflow-y-auto p-2">
            {filteredConversations.length === 0 ? (
              <EmptyPanel>Nenhuma conversa real encontrada. Conecte WhatsApp, Instagram, Messenger ou Website Chat para receber mensagens.</EmptyPanel>
            ) : filteredConversations.map((conversation) => (
              <button
                key={conversation.id}
                type="button"
                onClick={() => setSelectedId(conversation.id)}
                className={`mb-2 flex w-full gap-3 rounded-lg border p-3 text-left transition ${selectedId === conversation.id ? 'border-violet-400/50 bg-violet-600/35' : 'border-transparent bg-white/[0.03] hover:border-white/10'}`}
              >
                <ChannelIcon channel={conversation.channel} />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-2">
                    <p className="truncate font-semibold text-white">{conversation.customer_name}</p>
                    <span className="text-xs text-slate-400">{timeLabel(conversation.last_message_at)}</span>
                  </div>
                  <p className="mt-1 truncate text-xs text-slate-400">{conversation.last_message_preview || 'Sem mensagens ainda.'}</p>
                  <p className="mt-2 text-[11px] text-violet-200">{conversation.ai_mode === 'ia' ? 'IA respondendo' : conversation.ai_mode === 'hibrido' ? 'Modo hibrido' : 'Humano'}</p>
                </div>
              </button>
            ))}
          </div>
        </aside>

        <section className="flex min-h-[720px] flex-col rounded-lg border border-white/10 bg-slate-950/55">
          {currentConversation ? (
            <>
              <div className="flex items-center justify-between border-b border-white/10 p-4">
                <div className="flex items-center gap-3">
                  <ChannelIcon channel={currentConversation.channel} />
                  <div>
                    <h2 className="font-display text-xl">{currentConversation.customer_name}</h2>
                    <p className="text-xs text-slate-400">{currentConversation.city ?? 'Cidade nao informada'} · Contato via {currentConversation.channel}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-slate-300">
                  <Star size={17} />
                  <UserPlus size={17} />
                  <Tag size={17} />
                  <MoreVertical size={17} />
                </div>
              </div>

              <div className="flex items-center justify-between border-b border-violet-400/20 bg-violet-600/20 px-4 py-3 text-sm">
                <span className="flex items-center gap-2"><Sparkles size={16} /> {currentConversation.ai_mode === 'ia' ? 'IA ativa nesta conversa' : currentConversation.ai_mode === 'hibrido' ? 'IA sugere e humano aprova' : 'Atendimento humano'}</span>
                <button type="button" onClick={handleSuggestions} className="rounded-lg border border-white/10 px-3 py-1 text-xs">Gerar sugestoes reais</button>
              </div>

              <div className="flex-1 space-y-4 overflow-y-auto bg-[radial-gradient(circle_at_20%_20%,rgba(124,58,237,0.10),transparent_28%)] p-4">
                {detailLoading ? (
                  <div className="grid h-full place-items-center"><Loader2 className="animate-spin text-cyan" /></div>
                ) : detail?.messages.length ? (
                  detail.messages.map((message) => <MessageBubble key={message.id} message={message} />)
                ) : (
                  <EmptyPanel>Sem mensagens reais nesta conversa.</EmptyPanel>
                )}
                {suggestions.length > 0 ? (
                  <div className="max-w-md rounded-lg border border-white/10 bg-slate-950/90 p-3">
                    <div className="mb-3 flex items-center justify-between text-sm">
                      <span className="flex items-center gap-2 font-semibold"><Sparkles size={15} /> IA sugeriu {suggestions.length} respostas</span>
                    </div>
                    <div className="space-y-2">
                      {suggestions.map((suggestion) => (
                        <button key={suggestion} type="button" onClick={() => setDraft(suggestion)} className="flex w-full items-center justify-between rounded-lg border border-white/10 px-3 py-2 text-left text-sm text-slate-200">
                          <span className="truncate">{suggestion}</span>
                          <ChevronRight size={15} />
                        </button>
                      ))}
                    </div>
                  </div>
                ) : null}
              </div>

              <form onSubmit={handleSubmit} className="border-t border-white/10 p-4">
                <div className="mb-3 flex gap-5 text-sm">
                  <span className="border-b border-violet-400 pb-2 text-white">Responder</span>
                  <span className="pb-2 text-slate-400">Nota interna</span>
                </div>
                <textarea
                  className="min-h-28 w-full resize-none rounded-lg border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500 focus:border-violet-400/60"
                  placeholder="Digite sua mensagem..."
                  value={draft}
                  onChange={(event) => setDraft(event.target.value)}
                />
                {sendError ? <p className="mt-2 text-sm text-amber-200">{sendError}</p> : null}
                <div className="mt-3 flex items-center justify-between gap-3">
                  <div className="flex flex-wrap gap-3 text-slate-400">
                    <Smile size={17} />
                    <Paperclip size={17} />
                    <Image size={17} />
                    <FileText size={17} />
                    <Link2 size={17} />
                    <CalendarDays size={17} />
                    <Zap size={17} />
                  </div>
                  <button type="submit" className="inline-flex items-center gap-2 rounded-lg bg-violet-600 px-5 py-3 text-sm font-semibold text-white disabled:opacity-50" disabled={!draft.trim()}>
                    Enviar <Send size={15} />
                  </button>
                </div>
              </form>
            </>
          ) : (
            <EmptyPanel>Selecione uma conversa real ou conecte um canal para iniciar atendimento.</EmptyPanel>
          )}
        </section>

        <aside className="space-y-3 rounded-lg border border-white/10 bg-slate-950/55 p-3">
          <section className="rounded-lg border border-white/10 bg-white/[0.03] p-4">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="font-display text-lg">Dados do cliente</h2>
              <MoreVertical size={16} className="text-slate-400" />
            </div>
            {currentConversation ? (
              <>
                <div className="flex gap-3">
                  <ChannelIcon channel={currentConversation.channel} />
                  <div>
                    <p className="font-semibold">{currentConversation.customer_name}</p>
                    <p className="text-xs text-slate-400">{currentConversation.phone ?? 'Telefone nao informado'}</p>
                    <p className="text-xs text-slate-400">{currentConversation.email ?? 'Email nao informado'}</p>
                  </div>
                </div>
                <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
                  <div className="rounded-lg bg-slate-950/65 p-3"><p className="text-slate-400">Conversas</p><p className="font-semibold">{summary?.total ?? 0}</p></div>
                  <div className="rounded-lg bg-slate-950/65 p-3"><p className="text-slate-400">Reservas</p><p className="font-semibold">{reservations.length}</p></div>
                  <div className="rounded-lg bg-slate-950/65 p-3"><p className="text-slate-400">Gasto total</p><p className="font-semibold">{money(totalSpent)}</p></div>
                  <div className="rounded-lg bg-slate-950/65 p-3"><p className="text-slate-400">Ultima reserva</p><p className="font-semibold">{dateLabel(reservations[0]?.check_in)}</p></div>
                </div>
              </>
            ) : <EmptyPanel>Sem cliente selecionado.</EmptyPanel>}
          </section>

          <section className="rounded-lg border border-white/10 bg-white/[0.03] p-4">
            <h2 className="font-display text-lg">Historico de reservas</h2>
            <div className="mt-3 space-y-2">
              {reservations.length === 0 ? <p className="text-sm text-slate-400">Sem historico de reservas para este cliente.</p> : reservations.map((item) => (
                <div key={item.id} className="rounded-lg border border-white/10 p-3 text-sm">
                  <p className="text-slate-300">{dateLabel(item.check_in)} a {dateLabel(item.check_out)}</p>
                  <p className="mt-1 flex justify-between"><span>{money(item.value)}</span><span className="text-emerald-300">{item.status}</span></p>
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-lg border border-white/10 bg-white/[0.03] p-4">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="font-display text-lg">Acoes rapidas</h2>
              <Clock size={15} className="text-slate-400" />
            </div>
            {['Criar reserva', 'Enviar orcamento', 'Enviar catalogo', 'Transferir conversa'].map((action) => (
              <button key={action} type="button" className="mb-2 flex w-full items-center gap-2 rounded-lg border border-white/10 px-3 py-2 text-left text-sm text-slate-200">
                <CircleDollarSign size={15} className="text-emerald-300" />
                {action}
              </button>
            ))}
          </section>

          <section className="rounded-lg border border-white/10 bg-white/[0.03] p-4">
            <h2 className="font-display text-lg">Informacoes da conversa</h2>
            <dl className="mt-3 space-y-2 text-sm">
              <div className="flex justify-between gap-3"><dt className="text-slate-400">Canal</dt><dd>{currentConversation?.channel ?? '-'}</dd></div>
              <div className="flex justify-between gap-3"><dt className="text-slate-400">Inicio</dt><dd>{dateLabel(currentConversation?.last_message_at)}</dd></div>
              <div className="flex justify-between gap-3"><dt className="text-slate-400">Atendente</dt><dd>{currentConversation?.assigned_to ?? 'Nao atribuido'}</dd></div>
              <div className="flex justify-between gap-3"><dt className="text-slate-400">Status</dt><dd>{currentConversation?.status ?? '-'}</dd></div>
              <div className="flex justify-between gap-3"><dt className="text-slate-400">Modo IA</dt><dd>{currentConversation?.ai_mode ?? '-'}</dd></div>
            </dl>
          </section>
        </aside>
      </div>
    </div>
  );
}
