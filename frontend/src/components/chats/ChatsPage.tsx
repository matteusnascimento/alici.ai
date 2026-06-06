import {
  ChevronRight,
  FileText,
  Image,
  Loader2,
  Mail,
  MessageCircle,
  MoreHorizontal,
  Paperclip,
  Phone,
  Search,
  Send,
  ShieldCheck,
  Smile,
  Sparkles,
  Star,
} from 'lucide-react';
import { FormEvent, useEffect, useMemo, useState } from 'react';

import { ApiError } from '../../services/api';
import {
  addConversationTag,
  createConversationTask,
  getAiSuggestions,
  getChatChannels,
  getChatSummary,
  getChatTags,
  getChatTeam,
  getCustomerReservations,
  getOmnichannelConversation,
  getOmnichannelConversations,
  sendConversationQuote,
  sendOmnichannelMessage,
  transferConversationToHuman,
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

const filters = [
  { key: 'all', label: 'Todas' },
  { key: 'human', label: 'Nao lidas' },
  { key: 'mine', label: 'Minhas' },
] as const;

const quickActions = [
  { key: 'quote', label: 'Criar cotacao' },
  { key: 'task', label: 'Criar tarefa' },
  { key: 'human', label: 'Transferir para Humano' },
  { key: 'ia', label: 'Ativar IA' },
  { key: 'tag', label: 'Adicionar tag' },
] as const;

const channelClass: Record<string, string> = {
  whatsapp: 'bg-emerald-500 text-white',
  instagram: 'bg-pink-500 text-white',
  website_chat: 'bg-violet-500 text-white',
};

const officialChannels = new Set(['whatsapp', 'instagram', 'website_chat']);

const channelLabels: Record<string, string> = {
  whatsapp: 'WhatsApp Business',
  instagram: 'Instagram Business',
  website_chat: 'Website Chat',
};

function timeLabel(value?: string | null) {
  if (!value) return '--:--';
  return new Date(value).toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}

function dateLabel(value?: string | null) {
  if (!value) return '-';
  return new Date(value).toLocaleDateString('pt-BR');
}

function money(value: number) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
}

function ChannelIcon({ channel }: { channel: string }) {
  return (
    <span className={`grid h-9 w-9 shrink-0 place-items-center rounded-xl ${channelClass[channel] ?? 'bg-slate-400 text-white'}`}>
      <MessageCircle size={18} />
    </span>
  );
}

function EmptyCard({ children }: { children: string }) {
  return (
    <div className="grid min-h-36 place-items-center rounded-2xl border border-dashed border-slate-200 bg-slate-50/80 p-6 text-center text-sm text-slate-500">
      {children}
    </div>
  );
}

function ConversationEmptyState() {
  return (
    <div className="grid min-h-full flex-1 place-items-center p-8">
      <div className="max-w-md text-center">
        <span className="mx-auto grid h-16 w-16 place-items-center rounded-2xl bg-violet-100 text-violet-700">
          <MessageCircle size={30} />
        </span>
        <h2 className="mt-5 font-display text-3xl text-slate-950">Nenhuma conversa selecionada</h2>
        <p className="mt-3 text-sm leading-6 text-slate-500">
          Conecte um canal para comecar a receber mensagens. O AXI centraliza WhatsApp Business, Instagram Business e Website Chat em um unico lugar.
        </p>
        <a href="/app/integrations" className="mt-5 inline-flex items-center justify-center rounded-xl bg-violet-600 px-5 py-3 text-sm font-semibold text-white shadow-sm shadow-violet-500/20">
          Conectar Integracoes
        </a>
        <p className="mt-4 text-xs text-slate-400">ou selecione uma conversa existente na lista lateral.</p>
      </div>
    </div>
  );
}

function MessageBubble({ message }: { message: OmnichannelMessage }) {
  const outgoing = message.sender_type === 'assistant' || message.sender_type === 'human';
  return (
    <article className={`max-w-[78%] rounded-2xl px-5 py-4 text-sm shadow-sm ${outgoing ? 'ml-auto bg-violet-100 text-slate-950' : 'border border-slate-200 bg-white text-slate-950'}`}>
      <p className="mb-1 text-xs font-semibold text-violet-700">{message.sender_type === 'assistant' ? 'AXI IA' : message.sender_type === 'human' ? 'Atendente' : 'Cliente'}</p>
      <p className="whitespace-pre-wrap leading-6">{message.content}</p>
      <p className="mt-2 text-right text-xs text-slate-400">{timeLabel(message.created_at)}</p>
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
  const [activeChannel, setActiveChannel] = useState('all');
  const [activeFilter, setActiveFilter] = useState<(typeof filters)[number]['key']>('all');
  const [mode, setMode] = useState<'ia' | 'humano' | 'hibrido'>('hibrido');
  const [draft, setDraft] = useState('');
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sendError, setSendError] = useState<string | null>(null);
  const [actionNotice, setActionNotice] = useState<string | null>(null);

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
          setChannels(channelData.filter((channel) => officialChannels.has(channel.key)));
          setTeam(teamData);
          setTags(tagData);
          setConversations(conversationData.filter((conversation) => officialChannels.has(conversation.channel)));
          setSelectedId(null);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Falha ao carregar Chats');
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
          setActionNotice(null);
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
      if (activeFilter === 'mine') return Boolean(conversation.assigned_to);
      if (activeFilter === 'human') return conversation.status === 'awaiting_human' || conversation.ai_mode === 'humano';
      return true;
    });
  }, [activeChannel, activeFilter, conversations]);

  const counts = {
    all: conversations.length,
    mine: conversations.filter((item) => item.assigned_to).length,
    human: conversations.filter((item) => item.status === 'awaiting_human' || item.ai_mode === 'humano').length,
  };
  const currentConversation = detail?.conversation ?? conversations.find((item) => item.id === selectedId) ?? null;
  const totalSpent = reservations.reduce((sum, item) => sum + item.value, 0);
  const renderedTags = detail?.tags?.length
    ? detail.tags.map((tag) => ({ id: String(tag.id), label: tag.tag, color: tag.color ?? 'violet' }))
    : tags;

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

  async function handleQuickAction(action: (typeof quickActions)[number]['key']) {
    if (!currentConversation) return;
    try {
      setSendError(null);
      setActionNotice(null);
      if (action === 'human') {
        const updated = await transferConversationToHuman(currentConversation.id);
        setMode(updated.ai_mode);
        setConversations((items) => items.map((item) => (item.id === updated.id ? { ...item, ...updated } : item)));
        setDetail((current) => current ? { ...current, conversation: { ...current.conversation, ...updated } } : current);
        return;
      }
      if (action === 'ia') {
        await handleModeChange('ia');
        return;
      }
      if (action === 'quote') {
        const response = await sendConversationQuote(currentConversation.id);
        setActionNotice(response.message);
        setDetail(await getOmnichannelConversation(currentConversation.id));
        return;
      }
      if (action === 'task') {
        await createConversationTask(currentConversation.id);
        setActionNotice('Tarefa criada para esta conversa.');
        setDetail(await getOmnichannelConversation(currentConversation.id));
        return;
      }
      await addConversationTag(currentConversation.id, 'follow_up');
      setActionNotice('Tag adicionada a conversa.');
      setDetail(await getOmnichannelConversation(currentConversation.id));
    } catch (err) {
      setSendError(err instanceof ApiError ? err.message : err instanceof Error ? err.message : 'Acao indisponivel');
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
      setDetail(await getOmnichannelConversation(currentConversation.id));
    } catch (err) {
      setSendError(err instanceof ApiError ? err.message : err instanceof Error ? err.message : 'Mensagem nao enviada');
    }
  }

  if (loading) {
    return <div className="grid min-h-[70vh] place-items-center"><Loader2 className="animate-spin text-violet-600" size={28} /></div>;
  }

  if (error) {
    return <div className="rounded-2xl border border-rose-200 bg-rose-50 p-5 text-rose-700">{error}</div>;
  }

  return (
    <div className="min-h-[calc(100vh-2rem)] rounded-[1.75rem] bg-[#f7f8ff] p-4 text-slate-950 shadow-[0_24px_90px_rgba(15,23,42,0.18)]">
      <header className="mb-4 flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
        <div className="flex items-center gap-3">
          <span className="grid h-11 w-11 place-items-center rounded-2xl bg-violet-600 text-white"><MessageCircle size={22} /></span>
          <div>
            <h1 className="font-display text-3xl">Chats</h1>
            <p className="text-sm text-slate-600">Atendimento Omnichannel</p>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <label className="flex min-w-[330px] items-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-500 shadow-sm">
            <Search size={18} />
            <span>Buscar conversas...</span>
            <span className="ml-auto text-xs text-slate-400">⌘ K</span>
          </label>
        </div>
      </header>

      <div className="grid gap-3 xl:grid-cols-[22%_minmax(520px,1fr)_20%]">
        <aside className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="font-display text-xl">Canais</h2>
            <a href="/app/integrations" className="grid h-9 w-9 place-items-center rounded-xl border border-slate-200 text-violet-700">+</a>
          </div>
          <div className="space-y-2">
            {channels.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-4 text-sm text-slate-500">
                <p className="font-semibold text-slate-700">Nenhum canal conectado</p>
                <p className="mt-2 leading-5">Conecte WhatsApp Business, Instagram Business ou Website Chat.</p>
                <a href="/app/integrations" className="mt-3 inline-flex rounded-xl bg-violet-600 px-4 py-2 text-xs font-semibold text-white">Ir para Integracoes</a>
              </div>
            ) : null}
            {channels.map((channel) => (
              <button
                key={channel.key}
                type="button"
                onClick={() => setActiveChannel(channel.key)}
                className={`flex w-full items-center gap-3 rounded-2xl px-3 py-3 text-left text-sm font-semibold transition ${activeChannel === channel.key ? 'bg-violet-50 text-violet-950' : 'hover:bg-slate-50'}`}
              >
                <ChannelIcon channel={channel.key} />
                <span className="flex-1">{channel.label}</span>
                <span className="rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-600">{channel.open_count}</span>
              </button>
            ))}
          </div>

          <div className="mt-5 border-t border-slate-100 pt-5">
            <h2 className="mb-3 font-display text-xl">Conversas</h2>
            <div className="mb-4 flex flex-wrap gap-2">
              {filters.map((filter) => (
                <button
                  key={filter.key}
                  type="button"
                  onClick={() => setActiveFilter(filter.key)}
                  className={`rounded-full px-4 py-2 text-xs font-semibold ${activeFilter === filter.key ? 'bg-violet-600 text-white' : 'bg-slate-100 text-slate-700'}`}
                >
                  {filter.label} {counts[filter.key]}
                </button>
              ))}
            </div>
            <div className="max-h-[calc(100vh-360px)] space-y-2 overflow-y-auto pr-1">
              {filteredConversations.length === 0 ? (
                <EmptyCard>Nenhuma conversa real encontrada. Conecte WhatsApp Business, Instagram Business ou Website Chat.</EmptyCard>
              ) : filteredConversations.map((conversation) => (
                <button
                  key={conversation.id}
                  type="button"
                  onClick={() => setSelectedId(conversation.id)}
                  className={`flex w-full gap-3 rounded-2xl p-3 text-left transition ${selectedId === conversation.id ? 'bg-violet-100' : 'hover:bg-slate-50'}`}
                >
                  <ChannelIcon channel={conversation.channel} />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center justify-between gap-2">
                      <p className="truncate font-bold">{conversation.customer_name}</p>
                      <span className="text-xs text-slate-500">{timeLabel(conversation.last_message_at)}</span>
                    </div>
                    <p className="mt-1 truncate text-xs text-slate-500">{conversation.last_message_preview || 'Sem mensagens ainda.'}</p>
                    <div className="mt-2 flex items-center justify-between gap-2">
                      <span className="truncate text-[11px] font-semibold text-slate-400">{channelLabels[conversation.channel] ?? conversation.channel}</span>
                      {conversation.unread_count > 0 ? (
                        <span className="grid h-5 min-w-5 place-items-center rounded-full bg-violet-600 px-1.5 text-[11px] font-bold text-white">{conversation.unread_count}</span>
                      ) : null}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </aside>

        <main className="flex min-h-[760px] flex-col rounded-2xl border border-slate-200 bg-white shadow-sm">
          {currentConversation ? (
            <>
              <div className="flex flex-col gap-3 border-b border-slate-100 p-4 lg:flex-row lg:items-start lg:justify-between">
                <div className="flex items-center gap-3">
                  <ChannelIcon channel={currentConversation.channel} />
                  <div>
                    <h2 className="font-display text-2xl">{currentConversation.customer_name}</h2>
                    <div className="mt-2 flex flex-wrap items-center gap-2 text-xs font-semibold text-slate-500">
                      <span className="rounded-full bg-slate-100 px-2.5 py-1">{channelLabels[currentConversation.channel] ?? currentConversation.channel}</span>
                      <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-emerald-700">{currentConversation.sales_stage ?? 'Lead quente'}</span>
                      <span>Ultima atividade {timeLabel(currentConversation.last_message_at)}</span>
                      <span>Origem: {currentConversation.source ?? 'Nao informada'}</span>
                    </div>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {renderedTags.slice(0, 3).map((tag) => (
                        <span key={tag.id} className="rounded-full bg-violet-50 px-2.5 py-1 text-[11px] font-bold text-violet-700">{tag.label}</span>
                      ))}
                    </div>
                    <p className="text-sm text-slate-500">{currentConversation.status} · {currentConversation.ai_mode}</p>
                  </div>
                </div>
                <div className="flex flex-wrap items-center justify-end gap-2">
                  <div className="inline-flex rounded-xl bg-slate-950 p-1 text-xs font-semibold text-white shadow-sm">
                    {(['ia', 'humano', 'hibrido'] as const).map((item) => (
                      <button
                        key={item}
                        type="button"
                        onClick={() => void handleModeChange(item)}
                        className={`rounded-lg px-3 py-2 capitalize ${mode === item ? 'bg-violet-600' : 'text-slate-300'}`}
                      >
                        {item === 'ia' ? 'IA' : item}
                      </button>
                    ))}
                  </div>
                  <button type="button" onClick={() => void handleQuickAction('human')} className="rounded-xl border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-700">Transferir</button>
                  <button type="button" onClick={() => void handleQuickAction('task')} className="rounded-xl border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-700">Criar tarefa</button>
                  <button type="button" onClick={() => void handleQuickAction('quote')} className="rounded-xl border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-700">Enviar cotacao</button>
                  <button type="button" onClick={() => void handleQuickAction('tag')} className="rounded-xl border border-slate-200 px-3 py-2 text-xs font-semibold text-slate-700">Adicionar tag</button>
                </div>
              </div>

              <div className="grid gap-3 border-b border-slate-100 p-4 md:grid-cols-4">
                <div className="rounded-xl bg-slate-50 p-3 text-sm"><p className="text-slate-500">Primeiro contato</p><p className="font-semibold">{dateLabel(currentConversation.last_message_at)}</p></div>
                <div className="rounded-xl bg-slate-50 p-3 text-sm"><p className="text-slate-500">Total de conversas</p><p className="font-semibold">{summary?.total ?? 0}</p></div>
                <div className="rounded-xl bg-slate-50 p-3 text-sm"><p className="text-slate-500">Ultima atividade</p><p className="font-semibold">{timeLabel(currentConversation.last_message_at)}</p></div>
                <div className="rounded-xl bg-slate-50 p-3 text-sm"><p className="text-slate-500">Responsavel</p><p className="font-semibold">{currentConversation.assigned_to ?? 'Nao atribuido'}</p></div>
              </div>

              <div className="flex-1 space-y-4 overflow-y-auto bg-[#fbfbff] p-5">
                {detailLoading ? <Loader2 className="mx-auto mt-20 animate-spin text-violet-600" /> : null}
                {!detailLoading && detail?.messages.length === 0 ? <EmptyCard>Sem mensagens reais nesta conversa.</EmptyCard> : null}
                {detail?.messages.map((message) => <MessageBubble key={message.id} message={message} />)}
                {suggestions.length > 0 ? (
                  <div className="max-w-lg rounded-2xl border border-violet-100 bg-white p-4 shadow-sm">
                    <p className="mb-3 flex items-center gap-2 font-bold text-violet-700"><Sparkles size={18} /> IA sugeriu {suggestions.length} respostas</p>
                    <div className="space-y-2">
                      {suggestions.map((suggestion) => (
                        <button key={suggestion} type="button" onClick={() => setDraft(suggestion)} className="flex w-full items-center justify-between rounded-xl border border-slate-100 px-3 py-2 text-left text-sm">
                          <span className="truncate">{suggestion}</span>
                          <ChevronRight size={15} />
                        </button>
                      ))}
                    </div>
                  </div>
                ) : null}
              </div>

              <form onSubmit={handleSubmit} className="border-t border-slate-100 p-4">
                <div className="mb-3 flex gap-6 text-sm font-semibold">
                  <span className="border-b-2 border-violet-600 pb-2 text-violet-700">Responder</span>
                  <span className="pb-2 text-slate-400">Nota interna</span>
                </div>
                <textarea
                  className="min-h-24 w-full resize-none rounded-2xl border border-slate-200 px-4 py-3 text-sm outline-none focus:border-violet-400"
                  placeholder="Digite sua mensagem..."
                  value={draft}
                  onChange={(event) => setDraft(event.target.value)}
                />
                {sendError ? <p className="mt-2 text-sm text-amber-600">{sendError}</p> : null}
                {actionNotice ? <p className="mt-2 text-sm text-emerald-600">{actionNotice}</p> : null}
                <div className="mt-3 flex items-center justify-between">
                  <div className="flex gap-3 text-slate-500">
                    <Paperclip size={18} /><Smile size={18} /><Image size={18} /><FileText size={18} /><Star size={18} />
                  </div>
                  <div className="flex gap-2">
                    <button type="button" onClick={handleSuggestions} className="inline-flex items-center gap-2 rounded-xl bg-violet-50 px-4 py-3 text-sm font-semibold text-violet-700">
                      <Sparkles size={16} /> IA
                    </button>
                    <button type="submit" disabled={!draft.trim()} className="grid h-12 w-14 place-items-center rounded-xl bg-violet-600 text-white disabled:opacity-50">
                      <Send size={20} />
                    </button>
                  </div>
                </div>
              </form>
            </>
          ) : (
            <ConversationEmptyState />
          )}
        </main>

        <aside className="space-y-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          {!currentConversation ? (
            <div className="grid min-h-[520px] place-items-center rounded-2xl border border-dashed border-slate-200 bg-slate-50/80 p-6 text-center">
              <div>
                <span className="mx-auto grid h-12 w-12 place-items-center rounded-2xl bg-violet-100 text-violet-700">
                  <ShieldCheck size={24} />
                </span>
                <h2 className="mt-4 font-display text-2xl">Nenhum cliente selecionado</h2>
                <p className="mt-2 text-sm leading-6 text-slate-500">Os dados do contato aparecerao aqui quando uma conversa for aberta.</p>
              </div>
            </div>
          ) : (
            <>
          <section>
            <div className="mb-4 flex items-center justify-between">
              <h2 className="font-display text-xl">Detalhes do contato</h2>
              <MoreHorizontal size={18} />
            </div>
            {currentConversation ? (
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <ChannelIcon channel={currentConversation.channel} />
                  <div>
                    <p className="font-bold">{currentConversation.customer_name}</p>
                    <p className="text-xs text-slate-500">Lead</p>
                  </div>
                </div>
                <div className="space-y-2 text-sm text-slate-600">
                  <p className="flex items-center gap-2"><Phone size={15} /> {currentConversation.phone ?? 'Telefone nao informado'}</p>
                  <p className="flex items-center gap-2"><Mail size={15} /> {currentConversation.email ?? 'Email nao informado'}</p>
                  <p className="flex items-center gap-2"><ShieldCheck size={15} /> {currentConversation.city ?? 'Cidade nao informada'}</p>
                </div>
                <div className="grid grid-cols-3 gap-2 text-sm">
                  <div className="rounded-xl bg-slate-50 p-3"><p className="text-slate-500">Ticket</p><p className="font-bold">{money(totalSpent)}</p></div>
                  <div className="rounded-xl bg-slate-50 p-3"><p className="text-slate-500">Reservas</p><p className="font-bold">{reservations.length}</p></div>
                  <div className="rounded-xl bg-slate-50 p-3"><p className="text-slate-500">Ultima</p><p className="font-bold">{dateLabel(reservations[0]?.check_in)}</p></div>
                </div>
              </div>
            ) : <EmptyCard>Sem contato selecionado.</EmptyCard>}
          </section>

          <section className="rounded-2xl border border-violet-100 p-4">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="font-bold">Historico de reservas</h3>
              <span className="text-xs text-violet-700">Ver todas</span>
            </div>
            {reservations.length === 0 ? (
              <p className="text-sm text-slate-500">Sem historico de reservas para este cliente.</p>
            ) : reservations.map((item) => (
              <div key={item.id} className="mb-2 rounded-xl bg-slate-50 p-3 text-sm">
                <p>{dateLabel(item.check_in)} a {dateLabel(item.check_out)}</p>
                <p className="mt-1 flex justify-between"><span>{money(item.value)}</span><span className="text-emerald-600">{item.status}</span></p>
              </div>
            ))}
          </section>

          <section className="rounded-2xl border border-slate-100 p-4">
            <h3 className="mb-3 font-bold">Tags</h3>
            <div className="flex flex-wrap gap-2">
              {renderedTags.map((tag) => (
                <span key={tag.id} className="rounded-full bg-violet-50 px-3 py-1 text-xs font-semibold text-violet-700">{tag.label}</span>
              ))}
            </div>
          </section>
            </>
          )}
        </aside>
      </div>
    </div>
  );
}
