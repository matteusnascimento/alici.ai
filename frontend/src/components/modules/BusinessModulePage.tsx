import {
  BarChart3,
  CalendarDays,
  ClipboardList,
  Contact,
  DollarSign,
  Filter,
  Handshake,
  Loader2,
  Megaphone,
  MessageSquare,
  Package,
  Phone,
  Plus,
  Search,
  Sparkles,
  Truck,
  Users,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { Navigate, useParams } from 'react-router-dom';

import {
  createBusinessResource,
  getBusinessSummary,
  listBusinessResource,
  type BusinessCall,
  type BusinessContact,
  type BusinessDeal,
  type BusinessGenericRecord,
  type BusinessPipeline,
  type BusinessProduct,
  type BusinessResource,
  type BusinessRevenueGoal,
  type BusinessSummary,
} from '../../services/business.service';

type ModuleGroup = 'crm' | 'cs' | 'analytics';
type ModuleId =
  | 'negocios' | 'pipelines' | 'contatos' | 'grupos' | 'reunioes'
  | 'produtos' | 'contratos' | 'agenda' | 'ligacoes' | 'mensagens-rapidas'
  | 'jornada' | 'logistica' | 'analises' | 'receita' | 'forecast';

interface ModuleDefinition {
  id: ModuleId;
  group: ModuleGroup;
  title: string;
  subtitle: string;
  purpose: string;
  actions: string[];
  createLabel?: string;
  icon: typeof Handshake;
  resource?: BusinessResource;
}

const modules: ModuleDefinition[] = [
  {
    id: 'negocios',
    group: 'crm',
    title: 'Negocios',
    subtitle: 'Pipeline comercial e oportunidades reais',
    purpose: 'Transformar conversas, contatos e produtos em oportunidades acompanhadas por etapa, valor e previsao de fechamento.',
    actions: ['Criar oportunidade', 'Acompanhar valor do pipeline', 'Enviar follow-up pelo chat'],
    createLabel: 'Novo negocio',
    icon: Handshake,
    resource: 'deals',
  },
  {
    id: 'pipelines',
    group: 'crm',
    title: 'Pipelines',
    subtitle: 'Gerencie funis de venda e suas etapas',
    purpose: 'Modelar o processo comercial da empresa para que equipe e IA entendam cada etapa da venda.',
    actions: ['Criar funil', 'Organizar etapas', 'Padronizar conversao'],
    createLabel: 'Novo pipeline',
    icon: Filter,
    resource: 'pipelines',
  },
  {
    id: 'contatos',
    group: 'crm',
    title: 'Contatos',
    subtitle: 'Base de leads e clientes vinda dos canais',
    purpose: 'Centralizar clientes, leads e contatos importados de WhatsApp, Instagram e demais canais para analise da IA.',
    actions: ['Ver lista', 'Adicionar contato', 'Abrir conversa'],
    icon: Contact,
    resource: 'contacts',
  },
  {
    id: 'grupos',
    group: 'crm',
    title: 'Grupos',
    subtitle: 'Segmentos para atendimento e campanhas',
    purpose: 'Separar contatos por interesse, origem ou perfil para campanhas e automacoes mais precisas.',
    actions: ['Criar grupo', 'Segmentar contatos', 'Preparar campanha'],
    createLabel: 'Novo grupo',
    icon: Users,
    resource: 'groups',
  },
  {
    id: 'reunioes',
    group: 'crm',
    title: 'Reunioes',
    subtitle: 'Retornos comerciais e compromissos',
    purpose: 'Registrar reunioes, retornos e compromissos comerciais para evitar perda de oportunidade.',
    actions: ['Agendar retorno', 'Registrar observacoes', 'Acompanhar status'],
    createLabel: 'Nova reuniao',
    icon: CalendarDays,
    resource: 'meetings',
  },
  {
    id: 'produtos',
    group: 'crm',
    title: 'Produtos',
    subtitle: 'Produtos e servicos usados pelos agentes',
    purpose: 'Cadastrar o catalogo que a IA pode consultar para responder duvidas, montar propostas e vender melhor.',
    actions: ['Cadastrar produto', 'Definir preco', 'Ativar oferta'],
    createLabel: 'Novo produto',
    icon: Package,
    resource: 'products',
  },
  {
    id: 'contratos',
    group: 'crm',
    title: 'Contratos',
    subtitle: 'Propostas aceitas e documentos',
    purpose: 'Acompanhar contratos, propostas e documentos ligados a clientes e negocios fechados.',
    actions: ['Criar contrato', 'Controlar valor', 'Acompanhar assinatura'],
    createLabel: 'Novo contrato',
    icon: ClipboardList,
    resource: 'contracts',
  },
  {
    id: 'agenda',
    group: 'crm',
    title: 'Agenda',
    subtitle: 'Tarefas, retornos e lembretes',
    purpose: 'Organizar acoes do time comercial e tarefas geradas pela IA a partir das conversas.',
    actions: ['Criar tarefa', 'Definir prioridade', 'Acompanhar prazo'],
    createLabel: 'Nova tarefa',
    icon: CalendarDays,
    resource: 'tasks',
  },
  {
    id: 'ligacoes',
    group: 'crm',
    title: 'Ligacoes',
    subtitle: 'Gestao e analise de ligacoes telefonicas',
    purpose: 'Registrar ligacoes, resultado da chamada e proximos passos para manter historico completo do cliente.',
    actions: ['Registrar ligacao', 'Anotar resultado', 'Medir atendimento'],
    createLabel: 'Nova ligacao',
    icon: Phone,
    resource: 'calls',
  },
  {
    id: 'mensagens-rapidas',
    group: 'crm',
    title: 'Mensagens Rapidas',
    subtitle: 'Respostas aprovadas para atendimento',
    purpose: 'Guardar respostas prontas e aprovadas para acelerar atendimento sem perder padronizacao.',
    actions: ['Criar resposta', 'Classificar por categoria', 'Usar no atendimento'],
    createLabel: 'Nova mensagem',
    icon: MessageSquare,
    resource: 'quick-messages',
  },
  {
    id: 'jornada',
    group: 'cs',
    title: 'Jornada',
    subtitle: 'Acompanhamento do ciclo do cliente',
    purpose: 'Controlar onboarding, sucesso e pendencias para reduzir churn e melhorar a experiencia do cliente.',
    actions: ['Criar etapa', 'Acompanhar pendencia', 'Priorizar cliente'],
    createLabel: 'Nova etapa',
    icon: ClipboardList,
    resource: 'tasks',
  },
  {
    id: 'logistica',
    group: 'cs',
    title: 'Logistica',
    subtitle: 'Operacao, entregas e status de servico',
    purpose: 'Acompanhar entregas, execucao de servicos e status operacional que impacta atendimento.',
    actions: ['Criar operacao', 'Informar rastreio', 'Atualizar status'],
    createLabel: 'Nova operacao',
    icon: Truck,
    resource: 'logistics',
  },
  {
    id: 'analises',
    group: 'analytics',
    title: 'Analises',
    subtitle: 'Indicadores de canais, IA e atendimento',
    purpose: 'Ler dados comerciais e de atendimento para mostrar gargalos, evolucao e oportunidades de melhoria.',
    actions: ['Ver indicadores', 'Comparar canais', 'Acompanhar operacao'],
    icon: BarChart3,
  },
  {
    id: 'receita',
    group: 'analytics',
    title: 'Receita',
    subtitle: 'Receita, creditos e conversao',
    purpose: 'Acompanhar receita realizada, metas mensais e ticket medio com base nos negocios fechados.',
    actions: ['Ver metas', 'Medir receita', 'Acompanhar ticket medio'],
    icon: DollarSign,
  },
  {
    id: 'forecast',
    group: 'analytics',
    title: 'Forecast',
    subtitle: 'Previsao baseada no pipeline real',
    purpose: 'Projetar receita futura com base no valor aberto, probabilidade e historico de fechamento.',
    actions: ['Projetar receita', 'Identificar risco', 'Planejar follow-up'],
    icon: BarChart3,
  },
];

const defaultByGroup: Record<ModuleGroup, ModuleId> = { crm: 'negocios', cs: 'jornada', analytics: 'analises' };

function money(cents = 0) {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(cents / 100);
}

function dateLabel(value?: string | null) {
  if (!value) return '-';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? '-' : date.toLocaleDateString('pt-BR');
}

function StatCard({ label, value, icon: Icon }: { label: string; value: string | number; icon: typeof Handshake }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
      <div className="flex items-center gap-2 text-xs text-slate-400"><Icon size={14} className="text-cyan" />{label}</div>
      <p className="mt-3 text-2xl font-bold text-[var(--text-primary)]">{value}</p>
    </div>
  );
}

function PurposePanel({ module }: { module: ModuleDefinition }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
      <p className="text-xs font-semibold uppercase tracking-[0.24em] text-cyan">Proposito do modulo</p>
      <p className="mt-2 max-w-4xl text-sm leading-6 text-slate-300">{module.purpose}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {module.actions.map((action) => (
          <span key={action} className="rounded-full border border-white/10 bg-black/20 px-3 py-1 text-xs text-slate-300">
            {action}
          </span>
        ))}
      </div>
    </div>
  );
}

function percent(value: number) {
  return `${Math.round(value)}%`;
}

function average(values: number[]) {
  if (!values.length) return 0;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function countGenericByStatus(items: BusinessGenericRecord[], status: string) {
  return items.filter((item) => String(item.status || '').toLowerCase() === status).length;
}

function ModuleStatsGrid({
  module,
  summary,
  contacts,
  deals,
  pipelines,
  products,
  calls,
  generic,
  goals,
}: {
  module: ModuleDefinition;
  summary: BusinessSummary | null;
  contacts: BusinessContact[];
  deals: BusinessDeal[];
  pipelines: BusinessPipeline[];
  products: BusinessProduct[];
  calls: BusinessCall[];
  generic: BusinessGenericRecord[];
  goals: BusinessRevenueGoal[];
}) {
  const openDeals = deals.filter((deal) => deal.status === 'open');
  const wonDeals = deals.filter((deal) => deal.status === 'won');
  const pipelineValue = summary?.pipeline_value_cents ?? openDeals.reduce((acc, item) => acc + (item.value_cents || 0), 0);
  const wonValue = summary?.won_value_cents ?? wonDeals.reduce((acc, item) => acc + (item.value_cents || 0), 0);
  const avgDeal = average(deals.map((deal) => deal.probability || 0));
  const avgTicket = wonDeals.length ? Math.round(wonValue / wonDeals.length) : 0;
  const currentMonth = new Date().getMonth() + 1;
  const currentGoal = goals.find((goal) => goal.month === currentMonth)?.target_cents || 0;
  const weightedForecast = openDeals.reduce((acc, deal) => acc + Math.round((deal.value_cents || 0) * ((deal.probability || 0) / 100)), 0);

  const statsByModule: Record<ModuleId, Array<{ label: string; value: string | number; icon: typeof Handshake }>> = {
    negocios: [
      { label: 'Oportunidades abertas', value: openDeals.length, icon: Handshake },
      { label: 'Valor em pipeline', value: money(pipelineValue), icon: DollarSign },
      { label: 'Fechados', value: wonDeals.length, icon: ClipboardList },
      { label: 'Probabilidade media', value: percent(avgDeal), icon: BarChart3 },
    ],
    pipelines: [
      { label: 'Funis criados', value: pipelines.length, icon: Filter },
      { label: 'Etapas mapeadas', value: pipelines.reduce((sum, pipeline) => sum + (pipeline.stages?.length || 0), 0), icon: ClipboardList },
      { label: 'Negocios abertos', value: openDeals.length, icon: Handshake },
      { label: 'Valor ativo', value: money(pipelineValue), icon: DollarSign },
    ],
    contatos: [
      { label: 'Total na base', value: contacts.length || summary?.contacts || 0, icon: Contact },
      { label: 'Origem WhatsApp', value: contacts.filter((contact) => String(contact.source || '').toLowerCase().includes('whatsapp')).length, icon: MessageSquare },
      { label: 'Prospects', value: contacts.filter((contact) => String(contact.status || '').toLowerCase() === 'prospect').length, icon: Users },
      { label: 'Com interacao', value: contacts.filter((contact) => Boolean(contact.last_interaction_at)).length, icon: CalendarDays },
    ],
    grupos: [
      { label: 'Grupos ativos', value: generic.length, icon: Users },
      { label: 'Contatos segmentados', value: contacts.length, icon: Contact },
      { label: 'Campanhas prontas', value: countGenericByStatus(generic, 'ready'), icon: Megaphone },
      { label: 'Pendentes', value: countGenericByStatus(generic, 'pending'), icon: ClipboardList },
    ],
    reunioes: [
      { label: 'Agendadas', value: generic.length, icon: CalendarDays },
      { label: 'Concluidas', value: countGenericByStatus(generic, 'done'), icon: ClipboardList },
      { label: 'Pendentes', value: countGenericByStatus(generic, 'scheduled') || countGenericByStatus(generic, 'open'), icon: CalendarDays },
      { label: 'Contatos envolvidos', value: contacts.length, icon: Contact },
    ],
    produtos: [
      { label: 'Itens cadastrados', value: products.length || summary?.products || 0, icon: Package },
      { label: 'Ativos', value: products.filter((product) => String(product.status || 'active') === 'active').length, icon: ClipboardList },
      { label: 'Ticket medio', value: money(Math.round(average(products.map((product) => product.price_cents || 0)))), icon: DollarSign },
      { label: 'Usados pela IA', value: products.length, icon: Sparkles },
    ],
    contratos: [
      { label: 'Contratos', value: generic.length, icon: ClipboardList },
      { label: 'Em rascunho', value: countGenericByStatus(generic, 'draft'), icon: ClipboardList },
      { label: 'Assinados', value: countGenericByStatus(generic, 'signed'), icon: Handshake },
      { label: 'Valor total', value: money(generic.reduce((sum, item) => sum + Number(item.value_cents || 0), 0)), icon: DollarSign },
    ],
    agenda: [
      { label: 'Tarefas abertas', value: generic.length, icon: CalendarDays },
      { label: 'Alta prioridade', value: generic.filter((item) => String(item.priority || '').toLowerCase() === 'high').length, icon: ClipboardList },
      { label: 'Concluidas', value: countGenericByStatus(generic, 'done'), icon: ClipboardList },
      { label: 'Hoje', value: generic.filter((item) => String(item.due_at || '').startsWith(new Date().toISOString().slice(0, 10))).length, icon: CalendarDays },
    ],
    ligacoes: [
      { label: 'Ligacoes registradas', value: calls.length || summary?.calls_today || 0, icon: Phone },
      { label: 'Duracao media', value: `${Math.round(average(calls.map((call) => call.duration_seconds || 0)))}s`, icon: CalendarDays },
      { label: 'Sem atendimento', value: calls.filter((call) => String(call.outcome || '').toLowerCase().includes('sem')).length, icon: Phone },
      { label: 'Com observacao', value: calls.filter((call) => Boolean(call.notes)).length, icon: MessageSquare },
    ],
    'mensagens-rapidas': [
      { label: 'Respostas prontas', value: generic.length, icon: MessageSquare },
      { label: 'Categorias', value: new Set(generic.map((item) => item.category).filter(Boolean)).size, icon: Filter },
      { label: 'Ativas', value: generic.filter((item) => String(item.status || 'active') === 'active').length, icon: ClipboardList },
      { label: 'Usadas no chat', value: generic.length, icon: MessageSquare },
    ],
    jornada: [
      { label: 'Clientes acompanhados', value: contacts.length, icon: Users },
      { label: 'Etapas abertas', value: generic.length, icon: ClipboardList },
      { label: 'Prioridade alta', value: generic.filter((item) => String(item.priority || '').toLowerCase() === 'high').length, icon: BarChart3 },
      { label: 'Concluidas', value: countGenericByStatus(generic, 'done'), icon: Handshake },
    ],
    logistica: [
      { label: 'Operacoes', value: generic.length, icon: Truck },
      { label: 'Em transito', value: countGenericByStatus(generic, 'in_transit'), icon: Truck },
      { label: 'Entregues', value: countGenericByStatus(generic, 'delivered'), icon: ClipboardList },
      { label: 'Pendentes', value: countGenericByStatus(generic, 'pending'), icon: CalendarDays },
    ],
    analises: [
      { label: 'Contatos analisados', value: contacts.length, icon: Contact },
      { label: 'Negocios analisados', value: deals.length, icon: Handshake },
      { label: 'Produtos monitorados', value: products.length, icon: Package },
      { label: 'Ligacoes mapeadas', value: calls.length, icon: Phone },
    ],
    receita: [
      { label: 'Receita realizada', value: money(wonValue), icon: DollarSign },
      { label: 'Meta do mes', value: money(currentGoal), icon: BarChart3 },
      { label: 'Fechamentos', value: wonDeals.length, icon: Handshake },
      { label: 'Ticket medio', value: money(avgTicket), icon: DollarSign },
    ],
    forecast: [
      { label: 'Forecast ponderado', value: money(weightedForecast), icon: BarChart3 },
      { label: 'Pipeline aberto', value: money(pipelineValue), icon: DollarSign },
      { label: 'Oportunidades', value: openDeals.length, icon: Handshake },
      { label: 'Probabilidade media', value: percent(avgDeal), icon: BarChart3 },
    ],
  };

  return (
    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
      {statsByModule[module.id].map((stat) => (
        <StatCard key={`${module.id}-${stat.label}`} {...stat} />
      ))}
    </div>
  );
}

function EmptyState({ title, action }: { title: string; action: string }) {
  return (
    <div className="flex min-h-[240px] flex-col items-center justify-center rounded-2xl border border-dashed border-white/10 bg-white/[0.02] p-8 text-center">
      <Package size={38} className="text-slate-600" />
      <p className="mt-4 text-sm font-semibold text-slate-300">{title}</p>
      <p className="mt-2 max-w-md text-xs leading-5 text-slate-500">{action}</p>
    </div>
  );
}

function CreatePanel({ module, onCreated }: { module: ModuleDefinition; onCreated: () => Promise<void> }) {
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState<Record<string, string>>({});
  const resource = module.resource;
  if (!resource) return null;

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!resource) return;
    setSaving(true);
    try {
      const payload: Record<string, unknown> = {};
      if (resource === 'contacts') Object.assign(payload, { name: form.name, phone: form.phone, email: form.email, company: form.company });
      if (resource === 'deals') Object.assign(payload, { title: form.title, value_cents: Math.round(Number(form.value || 0) * 100) });
      if (resource === 'pipelines') Object.assign(payload, { name: form.name, description: form.description });
      if (resource === 'products') Object.assign(payload, { name: form.name, description: form.description, price_cents: Math.round(Number(form.price || 0) * 100) });
      if (resource === 'calls') Object.assign(payload, { phone: form.phone, notes: form.notes });
      if (resource === 'groups') Object.assign(payload, { name: form.name, description: form.description });
      if (resource === 'meetings') Object.assign(payload, { title: form.title, scheduled_at: form.date, notes: form.notes, status: 'scheduled' });
      if (resource === 'contracts') Object.assign(payload, { title: form.title, value_cents: Math.round(Number(form.value || 0) * 100), status: 'draft' });
      if (resource === 'tasks') Object.assign(payload, { title: form.title, due_at: form.date, priority: form.priority || 'medium', status: 'open' });
      if (resource === 'quick-messages') Object.assign(payload, { title: form.title, body: form.body, category: form.category || 'atendimento' });
      if (resource === 'logistics') Object.assign(payload, { title: form.title, tracking_code: form.tracking_code, notes: form.notes });
      await createBusinessResource(resource, payload);
      setForm({});
      setOpen(false);
      await onCreated();
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-3">
      <button type="button" onClick={() => setOpen((v) => !v)} className="inline-flex items-center gap-2 rounded-xl bg-cyan px-4 py-2 text-sm font-semibold text-ink shadow-[0_14px_32px_rgb(var(--accent-rgb)/0.25)] transition hover:opacity-90">
        <Plus size={16} /> {module.createLabel || 'Novo registro'}
      </button>
      {open ? (
        <form onSubmit={(e) => void submit(e)} className="grid gap-3 rounded-2xl border border-white/10 bg-white/[0.03] p-4 md:grid-cols-2">
          {['contacts', 'pipelines', 'products', 'groups'].includes(resource) ? <input required placeholder="Nome" value={form.name ?? ''} onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))} className="rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm outline-none focus:border-cyan/50" /> : null}
          {['deals', 'meetings', 'contracts', 'tasks', 'quick-messages', 'logistics'].includes(resource) ? <input required placeholder="Titulo" value={form.title ?? ''} onChange={(e) => setForm((p) => ({ ...p, title: e.target.value }))} className="rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm outline-none focus:border-cyan/50" /> : null}
          {['deals', 'products', 'contracts'].includes(resource) ? <input placeholder="Valor em R$" type="number" min="0" step="0.01" value={form.value ?? form.price ?? ''} onChange={(e) => setForm((p) => ({ ...p, [resource === 'products' ? 'price' : 'value']: e.target.value }))} className="rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm outline-none focus:border-cyan/50" /> : null}
          {resource === 'contacts' ? <><input placeholder="Telefone" value={form.phone ?? ''} onChange={(e) => setForm((p) => ({ ...p, phone: e.target.value }))} className="rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm outline-none focus:border-cyan/50" /><input placeholder="Email" value={form.email ?? ''} onChange={(e) => setForm((p) => ({ ...p, email: e.target.value }))} className="rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm outline-none focus:border-cyan/50" /><input placeholder="Empresa" value={form.company ?? ''} onChange={(e) => setForm((p) => ({ ...p, company: e.target.value }))} className="rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm outline-none focus:border-cyan/50" /></> : null}
          {resource === 'calls' ? <><input required placeholder="Telefone" value={form.phone ?? ''} onChange={(e) => setForm((p) => ({ ...p, phone: e.target.value }))} className="rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm outline-none focus:border-cyan/50" /><input placeholder="Observacao" value={form.notes ?? ''} onChange={(e) => setForm((p) => ({ ...p, notes: e.target.value }))} className="rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm outline-none focus:border-cyan/50" /></> : null}
          {['meetings', 'tasks'].includes(resource) ? <input placeholder="Data" type="datetime-local" value={form.date ?? ''} onChange={(e) => setForm((p) => ({ ...p, date: e.target.value }))} className="rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm outline-none focus:border-cyan/50" /> : null}
          {resource === 'logistics' ? <input placeholder="Codigo de rastreio" value={form.tracking_code ?? ''} onChange={(e) => setForm((p) => ({ ...p, tracking_code: e.target.value }))} className="rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm outline-none focus:border-cyan/50" /> : null}
          {resource === 'quick-messages' ? <textarea required placeholder="Texto aprovado" value={form.body ?? ''} onChange={(e) => setForm((p) => ({ ...p, body: e.target.value }))} className="md:col-span-2 rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm outline-none focus:border-cyan/50" /> : null}
          {['pipelines', 'products', 'groups', 'meetings', 'logistics'].includes(resource) ? <textarea placeholder="Descricao ou observacoes" value={form.description ?? form.notes ?? ''} onChange={(e) => setForm((p) => ({ ...p, [resource === 'meetings' || resource === 'logistics' ? 'notes' : 'description']: e.target.value }))} className="md:col-span-2 rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm outline-none focus:border-cyan/50" /> : null}
          <button disabled={saving} className="md:col-span-2 inline-flex justify-center rounded-xl border border-cyan/30 bg-cyan/10 px-4 py-2 text-sm font-semibold text-cyan disabled:opacity-60">{saving ? <Loader2 size={16} className="animate-spin" /> : 'Salvar'}</button>
        </form>
      ) : null}
    </div>
  );
}

export function BusinessModulePage({ group }: { group: ModuleGroup }) {
  const { moduleId } = useParams();
  const current = modules.find((item) => item.group === group && item.id === (moduleId || defaultByGroup[group]));
  const [summary, setSummary] = useState<BusinessSummary | null>(null);
  const [contacts, setContacts] = useState<BusinessContact[]>([]);
  const [deals, setDeals] = useState<BusinessDeal[]>([]);
  const [pipelines, setPipelines] = useState<BusinessPipeline[]>([]);
  const [products, setProducts] = useState<BusinessProduct[]>([]);
  const [calls, setCalls] = useState<BusinessCall[]>([]);
  const [generic, setGeneric] = useState<BusinessGenericRecord[]>([]);
  const [goals, setGoals] = useState<BusinessRevenueGoal[]>([]);
  const [search, setSearch] = useState('');
  const [contactTab, setContactTab] = useState<'list' | 'add'>('list');
  const [loading, setLoading] = useState(true);

  async function reload() {
    setLoading(true);
    try {
      const activeResource = current?.resource;
      const [s, c, d, p, pr, ca, extra, rg] = await Promise.all([
        getBusinessSummary(),
        listBusinessResource<BusinessContact>('contacts', search),
        listBusinessResource<BusinessDeal>('deals', search),
        listBusinessResource<BusinessPipeline>('pipelines', search),
        listBusinessResource<BusinessProduct>('products', search),
        listBusinessResource<BusinessCall>('calls'),
        activeResource && !['contacts', 'deals', 'pipelines', 'products', 'calls'].includes(activeResource) ? listBusinessResource<BusinessGenericRecord>(activeResource, search) : Promise.resolve([]),
        listBusinessResource<BusinessRevenueGoal>('revenue-goals'),
      ]);
      setSummary(s); setContacts(c); setDeals(d); setPipelines(p); setProducts(pr); setCalls(ca); setGeneric(extra); setGoals(rg);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void reload(); }, [moduleId]);

  if (!current) return <Navigate replace to={`/app/${group}/${defaultByGroup[group]}`} />;
  const activeModule = current;
  const Icon = activeModule.icon;
  function renderList() {
    if (loading) return <div className="flex h-48 items-center justify-center"><Loader2 className="animate-spin text-cyan" /></div>;
    if (activeModule.id === 'contatos') {
      return (
        <ContactsModule
          contacts={contacts}
          loading={loading}
          onCreated={reload}
          tab={contactTab}
          onTabChange={setContactTab}
        />
      );
    }
    if (activeModule.id === 'negocios') return deals.length ? <DealGrid deals={deals} /> : <EmptyState title="Nenhum negocio cadastrado" action="Crie oportunidades reais ou transforme conversas em pipeline." />;
    if (activeModule.id === 'pipelines') return pipelines.length ? <PipelineView pipelines={pipelines} /> : <EmptyState title="Nenhum pipeline ainda" action="Crie seu primeiro funil para organizar vendas." />;
    if (activeModule.id === 'produtos') return products.length ? <ProductGrid products={products} /> : <EmptyState title="Nenhum produto cadastrado" action="Cadastre ofertas para a IA vender com precisao." />;
    if (activeModule.id === 'ligacoes') return calls.length ? <CallList calls={calls} /> : <EmptyState title="Nenhuma ligacao encontrada" action="Registre chamadas para analisar atendimento e follow-up." />;
    if (activeModule.id === 'analises') return <AnalyticsOverview contacts={contacts} deals={deals} products={products} calls={calls} />;
    if (activeModule.id === 'receita') return <RevenueTable deals={deals} goals={goals} />;
    if (activeModule.id === 'forecast') return <ForecastView deals={deals} />;
    return generic.length ? <GenericGrid items={generic} /> : <EmptyState title={`Nenhum registro em ${activeModule.title.toLowerCase()}`} action="Cadastre o primeiro item para ativar este modulo com dados reais." />;
  }

  return (
    <section className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div><div className="flex items-center gap-3"><Icon size={28} className="text-cyan" /><h1 className="font-display text-3xl font-bold text-[var(--text-primary)]">{activeModule.title}</h1></div><p className="mt-2 text-sm text-slate-400">{activeModule.subtitle}</p></div>
        {activeModule.id === 'contatos' ? null : <CreatePanel module={activeModule} onCreated={reload} />}
      </div>
      <PurposePanel module={activeModule} />
      <ModuleStatsGrid
        module={activeModule}
        summary={summary}
        contacts={contacts}
        deals={deals}
        pipelines={pipelines}
        products={products}
        calls={calls}
        generic={generic}
        goals={goals}
      />
      <div className="flex flex-col gap-3 rounded-2xl border border-white/10 bg-white/[0.03] p-3 md:flex-row">
        <div className="flex flex-1 items-center gap-2 rounded-xl border border-white/10 bg-black/20 px-3"><Search size={16} className="text-slate-500" /><input value={search} onChange={(e) => setSearch(e.target.value)} onKeyDown={(e) => { if (e.key === 'Enter') void reload(); }} placeholder={`Buscar em ${activeModule.title.toLowerCase()}`} className="h-11 flex-1 bg-transparent text-sm outline-none placeholder:text-slate-500" /></div>
        <button onClick={() => void reload()} className="rounded-xl border border-white/10 px-4 py-2 text-sm font-semibold text-slate-200 hover:border-cyan/40 hover:text-cyan">Buscar</button>
      </div>
      {renderList()}
    </section>
  );
}

function DealGrid({ deals }: { deals: BusinessDeal[] }) {
  const fallbackStages = ['Novo lead', 'Qualificacao', 'Proposta', 'Negociacao', 'Fechado'];
  const stages = Array.from(new Set([...fallbackStages, ...deals.map((deal) => deal.stage).filter(Boolean)]));
  return (
    <div className="overflow-x-auto pb-2">
      <div className="grid min-w-[980px] gap-3" style={{ gridTemplateColumns: `repeat(${stages.length}, minmax(210px, 1fr))` }}>
        {stages.map((stage) => {
          const stageDeals = deals.filter((deal) => deal.stage === stage);
          const total = stageDeals.reduce((sum, deal) => sum + (deal.value_cents || 0), 0);
          return (
            <section key={stage} className="rounded-2xl border border-white/10 bg-white/[0.025] p-3">
              <div className="mb-3">
                <div className="flex items-center justify-between gap-2">
                  <h3 className="text-sm font-bold text-white">{stage}</h3>
                  <span className="rounded-full bg-white/[0.06] px-2 py-0.5 text-[11px] text-slate-400">{stageDeals.length}</span>
                </div>
                <p className="mt-1 text-xs font-semibold text-cyan">{money(total)}</p>
              </div>
              <div className="space-y-2">
                {stageDeals.length ? stageDeals.map((deal) => (
                  <article key={deal.id} className="rounded-2xl border border-white/10 bg-black/25 p-3 shadow-sm">
                    <p className="line-clamp-2 text-sm font-semibold text-white">{deal.title}</p>
                    <p className="mt-2 text-lg font-black text-cyan">{money(deal.value_cents)}</p>
                    <div className="mt-3 flex items-center justify-between text-[11px] text-slate-500">
                      <span>{deal.status}</span>
                      <span>{deal.probability}%</span>
                    </div>
                  </article>
                )) : (
                  <div className="rounded-2xl border border-dashed border-white/10 px-3 py-8 text-center text-xs text-slate-500">
                    Sem negocios nesta etapa
                  </div>
                )}
              </div>
            </section>
          );
        })}
      </div>
    </div>
  );
}

function PipelineView({ pipelines }: { pipelines: BusinessPipeline[] }) {
  return <div className="grid gap-4 lg:grid-cols-[360px_1fr]"><div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5"><h3 className="font-semibold text-white">Seus pipelines</h3><div className="mt-4 space-y-2">{pipelines.map((p) => <div key={p.id} className="rounded-xl border border-white/10 bg-black/20 p-3 text-sm text-slate-300">{p.name}</div>)}</div></div><div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5"><h3 className="font-semibold text-white">Etapas</h3><div className="mt-4 flex flex-wrap gap-2">{(pipelines[0]?.stages || []).map((s) => <span key={s} className="rounded-full border border-cyan/25 bg-cyan/10 px-3 py-1 text-xs text-cyan">{s}</span>)}</div></div></div>;
}

function ContactsModule({
  contacts,
  loading,
  tab,
  onTabChange,
  onCreated,
}: {
  contacts: BusinessContact[];
  loading: boolean;
  tab: 'list' | 'add';
  onTabChange: (tab: 'list' | 'add') => void;
  onCreated: () => Promise<void>;
}) {
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ name: '', phone: '', email: '', company: '' });

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      await createBusinessResource<BusinessContact>('contacts', {
        name: form.name,
        phone: form.phone,
        email: form.email,
        company: form.company,
        source: 'manual',
      });
      setForm({ name: '', phone: '', email: '', company: '' });
      onTabChange('list');
      await onCreated();
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-2 rounded-2xl border border-white/10 bg-white/[0.03] p-2">
        <button
          type="button"
          onClick={() => onTabChange('list')}
          className={[
            'rounded-xl px-4 py-2 text-sm font-semibold transition',
            tab === 'list' ? 'bg-cyan text-ink' : 'text-slate-300 hover:bg-white/[0.06] hover:text-white',
          ].join(' ')}
        >
          Lista de contatos
        </button>
        <button
          type="button"
          onClick={() => onTabChange('add')}
          className={[
            'rounded-xl px-4 py-2 text-sm font-semibold transition',
            tab === 'add' ? 'bg-cyan text-ink' : 'text-slate-300 hover:bg-white/[0.06] hover:text-white',
          ].join(' ')}
        >
          Adicionar contato
        </button>
      </div>

      {tab === 'add' ? (
        <form onSubmit={(e) => void submit(e)} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
          <div className="mb-5">
            <h3 className="font-semibold text-white">Novo contato</h3>
            <p className="mt-1 text-sm text-slate-400">
              Cadastre leads, clientes ou contatos operacionais. Contatos vindos dos canais sociais tambem entram aqui automaticamente.
            </p>
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <input required placeholder="Nome do contato" value={form.name} onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))} className="rounded-xl border border-white/10 bg-black/20 px-3 py-3 text-sm outline-none focus:border-cyan/50" />
            <input placeholder="Telefone" value={form.phone} onChange={(e) => setForm((p) => ({ ...p, phone: e.target.value }))} className="rounded-xl border border-white/10 bg-black/20 px-3 py-3 text-sm outline-none focus:border-cyan/50" />
            <input placeholder="Email" value={form.email} onChange={(e) => setForm((p) => ({ ...p, email: e.target.value }))} className="rounded-xl border border-white/10 bg-black/20 px-3 py-3 text-sm outline-none focus:border-cyan/50" />
            <input placeholder="Empresa ou origem" value={form.company} onChange={(e) => setForm((p) => ({ ...p, company: e.target.value }))} className="rounded-xl border border-white/10 bg-black/20 px-3 py-3 text-sm outline-none focus:border-cyan/50" />
          </div>
          <div className="mt-4 flex justify-end">
            <button disabled={saving} className="inline-flex min-w-32 justify-center rounded-xl bg-cyan px-5 py-2.5 text-sm font-semibold text-ink disabled:opacity-60">
              {saving ? <Loader2 size={16} className="animate-spin" /> : 'Salvar contato'}
            </button>
          </div>
        </form>
      ) : loading ? (
        <div className="flex h-48 items-center justify-center"><Loader2 className="animate-spin text-cyan" /></div>
      ) : contacts.length ? (
        <ContactsTable contacts={contacts} />
      ) : (
        <EmptyState title="Nenhum contato cadastrado" action="Use a aba Adicionar contato ou conecte WhatsApp/Instagram para popular a base automaticamente." />
      )}
    </div>
  );
}

function ContactsTable({ contacts }: { contacts: BusinessContact[] }) {
  return <div className="overflow-hidden rounded-2xl border border-white/10"><table className="w-full min-w-[760px] text-left text-sm"><thead className="bg-white/[0.04] text-xs uppercase tracking-wide text-slate-400"><tr><th className="p-4">Nome / telefone</th><th>Status</th><th>Canais</th><th>Ultima interacao</th><th>Acoes</th></tr></thead><tbody>{contacts.map((c) => <tr key={c.id} className="border-t border-white/10"><td className="p-4"><p className="font-semibold text-white">{c.name}</p><p className="text-slate-500">{c.phone || c.email || '-'}</p></td><td><span className="rounded-lg border border-cyan/25 bg-cyan/10 px-2 py-1 text-xs text-cyan">{c.status}</span></td><td className="text-slate-400">{c.source || 'manual'}</td><td className="text-slate-400">{dateLabel(c.last_interaction_at)}</td><td><button className="rounded-xl bg-cyan px-3 py-2 text-ink"><MessageSquare size={16} /></button></td></tr>)}</tbody></table></div>;
}

function ProductGrid({ products }: { products: BusinessProduct[] }) {
  return <div className="grid gap-3 lg:grid-cols-3">{products.map((p) => <article key={p.id} className="rounded-2xl border border-white/10 bg-white/[0.03] p-4"><Package size={20} className="text-cyan" /><p className="mt-3 font-semibold text-white">{p.name}</p><p className="mt-1 text-sm text-slate-400">{p.description || 'Sem descricao'}</p><p className="mt-4 text-xl font-bold text-cyan">{money(p.price_cents)}</p></article>)}</div>;
}

function CallList({ calls }: { calls: BusinessCall[] }) {
  return <div className="space-y-2">{calls.map((c) => <div key={c.id} className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.03] p-4"><div><p className="font-semibold text-white">{c.phone}</p><p className="text-sm text-slate-500">{c.notes || c.outcome}</p></div><span className="text-sm text-slate-400">{c.duration_seconds}s</span></div>)}</div>;
}

function GenericGrid({ items }: { items: BusinessGenericRecord[] }) {
  return <div className="grid gap-3 lg:grid-cols-2 xl:grid-cols-3">{items.map((item) => <article key={item.id} className="rounded-2xl border border-white/10 bg-white/[0.03] p-4"><div className="flex items-start justify-between gap-3"><div><p className="font-semibold text-white">{item.title || item.name}</p><p className="mt-1 text-sm text-slate-500">{item.description || item.body || item.notes || item.tracking_code || 'Sem detalhes adicionais'}</p></div><span className="rounded-lg border border-cyan/25 bg-cyan/10 px-2 py-1 text-xs text-cyan">{item.status || 'ativo'}</span></div>{item.value_cents ? <p className="mt-4 text-xl font-bold text-cyan">{money(item.value_cents)}</p> : null}<p className="mt-4 text-xs text-slate-500">{dateLabel(item.scheduled_at || item.due_at || item.created_at)}</p></article>)}</div>;
}

function AnalyticsOverview({
  contacts,
  deals,
  products,
  calls,
}: {
  contacts: BusinessContact[];
  deals: BusinessDeal[];
  products: BusinessProduct[];
  calls: BusinessCall[];
}) {
  const wonDeals = deals.filter((deal) => deal.status === 'won');
  const openDeals = deals.filter((deal) => deal.status === 'open');
  const whatsappContacts = contacts.filter((contact) => String(contact.source || '').toLowerCase().includes('whatsapp')).length;
  const insights = [
    {
      title: 'Origem dos contatos',
      value: whatsappContacts ? `${whatsappContacts} via WhatsApp` : 'Sem canal dominante',
      text: 'Conecte redes sociais para a IA comparar origem, volume e qualidade dos leads.',
    },
    {
      title: 'Pipeline comercial',
      value: `${openDeals.length} abertos / ${wonDeals.length} ganhos`,
      text: 'Acompanhe conversas que viram oportunidade e veja onde o atendimento perde velocidade.',
    },
    {
      title: 'Catalogo e atendimento',
      value: `${products.length} produtos / ${calls.length} ligacoes`,
      text: 'Produtos completos ajudam a IA responder melhor e reduzem retrabalho do time.',
    },
  ];

  return (
    <div className="grid gap-4 xl:grid-cols-3">
      {insights.map((item) => (
        <article key={item.title} className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan">{item.title}</p>
          <p className="mt-3 text-2xl font-bold text-white">{item.value}</p>
          <p className="mt-3 text-sm leading-6 text-slate-400">{item.text}</p>
        </article>
      ))}
    </div>
  );
}

function ForecastView({ deals }: { deals: BusinessDeal[] }) {
  const openDeals = deals.filter((deal) => deal.status === 'open');
  const rows = openDeals.map((deal) => ({
    ...deal,
    weighted: Math.round((deal.value_cents || 0) * ((deal.probability || 0) / 100)),
  }));
  const totalWeighted = rows.reduce((sum, deal) => sum + deal.weighted, 0);

  if (!rows.length) {
    return <EmptyState title="Sem oportunidades para forecast" action="Crie negocios com valor e probabilidade para projetar receita futura." />;
  }

  return (
    <div className="space-y-4">
      <div className="rounded-2xl border border-cyan/20 bg-cyan/10 p-5">
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan">Previsao ponderada</p>
        <p className="mt-2 text-3xl font-black text-white">{money(totalWeighted)}</p>
        <p className="mt-2 text-sm text-slate-300">Calculado com valor do negocio multiplicado pela probabilidade atual.</p>
      </div>
      <div className="overflow-hidden rounded-2xl border border-white/10">
        <table className="w-full min-w-[760px] text-left text-sm">
          <thead className="bg-white/[0.04] text-xs uppercase tracking-wide text-slate-400">
            <tr><th className="p-4">Negocio</th><th>Etapa</th><th>Valor</th><th>Probabilidade</th><th>Forecast</th><th>Previsao</th></tr>
          </thead>
          <tbody>
            {rows.map((deal) => (
              <tr key={deal.id} className="border-t border-white/10">
                <td className="p-4 font-semibold text-white">{deal.title}</td>
                <td className="text-slate-400">{deal.stage}</td>
                <td className="font-semibold text-white">{money(deal.value_cents)}</td>
                <td className="text-cyan">{deal.probability}%</td>
                <td className="font-semibold text-white">{money(deal.weighted)}</td>
                <td className="text-slate-400">{dateLabel(deal.expected_close_date)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function RevenueTable({ deals, goals }: { deals: BusinessDeal[]; goals: BusinessRevenueGoal[] }) {
  const months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
  const year = new Date().getFullYear();
  const goalMap = new Map(goals.map((goal) => [`${goal.year}-${goal.month}`, goal.target_cents]));
  const rows = months.map((month, index) => {
    const monthNumber = index + 1;
    const wonDeals = deals.filter((deal) => deal.status === 'won' && new Date(deal.created_at || '').getMonth() + 1 === monthNumber);
    const won = wonDeals.reduce((acc, deal) => acc + (deal.value_cents || 0), 0);
    const target = goalMap.get(`${year}-${monthNumber}`) || 0;
    return { month, won, target, closes: wonDeals.length, pct: target ? Math.round((won / target) * 100) : 0 };
  });
  return <div className="space-y-4"><div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5"><h3 className="font-semibold text-white">Receita mensal vs meta</h3><div className="mt-6 grid h-48 grid-cols-12 items-end gap-2 border-b border-white/10">{rows.map((r) => <div key={r.month} className="flex h-full flex-col justify-end gap-2"><div className="rounded-t-lg bg-cyan/70" style={{ height: `${Math.max(2, Math.min(100, r.target ? (r.won / r.target) * 100 : r.won ? 30 : 2))}%` }} /><span className="text-center text-[10px] text-slate-500">{r.month}</span></div>)}</div></div><div className="overflow-hidden rounded-2xl border border-white/10"><table className="w-full min-w-[760px] text-left text-sm"><thead className="bg-white/[0.04] text-xs uppercase tracking-wide text-slate-400"><tr><th className="p-4">Mes</th><th>Receita</th><th>Meta</th><th>% Atingido</th><th>Fechamentos</th><th>Ticket medio</th></tr></thead><tbody>{rows.map((r) => <tr key={r.month} className="border-t border-white/10"><td className="p-4 font-semibold text-white">{r.month}</td><td className="font-semibold text-white">{money(r.won)}</td><td className="text-slate-400">{money(r.target)}</td><td><span className="text-cyan">{r.pct}%</span></td><td className="text-slate-300">{r.closes}</td><td className="font-semibold text-white">{money(r.closes ? Math.round(r.won / r.closes) : 0)}</td></tr>)}</tbody></table></div></div>;
}

