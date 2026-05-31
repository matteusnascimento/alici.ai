import {
  BarChart3,
  Bell,
  Bot,
  CalendarDays,
  CheckCircle2,
  ChevronDown,
  CircleDollarSign,
  Clock3,
  FileSpreadsheet,
  FileText,
  HelpCircle,
  Instagram,
  Loader2,
  Megaphone,
  MoreVertical,
  Plus,
  Search,
  Send,
  ShoppingCart,
  Target,
  TrendingUp,
  Users,
  Wand2,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';

import { listProjects } from '../../services/marketing.service';
import type { MarketingProject } from '../../types/marketing';

const marketingViews = [
  { key: 'overview', label: 'Visao Geral' },
  { key: 'action-plan', label: 'Plano de Acao' },
  { key: 'campaigns', label: 'Campanhas' },
  { key: 'calendar', label: 'Calendario' },
  { key: 'content', label: 'Conteudo' },
  { key: 'audiences', label: 'Audiencias' },
  { key: 'automations', label: 'Automacoes' },
  { key: 'reports', label: 'Relatorios' },
  { key: 'insights', label: 'Insights IA' },
] as const;

type MarketingView = (typeof marketingViews)[number]['key'];

const kpiCards: Array<{ label: string; icon: LucideIcon; tone: string; empty: string }> = [
  { label: 'Investimento', icon: CircleDollarSign, tone: 'from-violet-600 to-purple-500', empty: 'Conecte Meta Ads ou Google Ads' },
  { label: 'Receita gerada', icon: TrendingUp, tone: 'from-blue-600 to-cyan-500', empty: 'Integre Revenue para medir' },
  { label: 'ROAS', icon: Target, tone: 'from-emerald-600 to-green-400', empty: 'Sem custo e receita reais' },
  { label: 'Leads gerados', icon: Users, tone: 'from-orange-600 to-amber-400', empty: 'Sem leads de campanha' },
  { label: 'Reservas geradas', icon: ShoppingCart, tone: 'from-cyan-600 to-teal-400', empty: 'Sem reservas atribuidas' },
];

const actionColumns = [
  { title: 'Planejado', tone: 'from-blue-500/20 to-blue-950/40' },
  { title: 'Executando', tone: 'from-amber-500/20 to-amber-950/30' },
  { title: 'Concluido', tone: 'from-emerald-500/20 to-emerald-950/30' },
];

function EmptyPanel({ children, min = 'min-h-36' }: { children: string; min?: string }) {
  return (
    <div className={`grid ${min} place-items-center rounded-2xl border border-dashed border-white/15 bg-white/[0.035] p-5 text-center text-sm text-slate-400`}>
      {children}
    </div>
  );
}

function KpiCard({ label, icon: Icon, tone, empty }: { label: string; icon: LucideIcon; tone: string; empty: string }) {
  return (
    <article className="min-h-[126px] rounded-2xl border border-white/10 bg-[linear-gradient(145deg,rgba(15,23,42,0.92),rgba(2,6,23,0.72))] p-5 shadow-[0_20px_60px_rgba(0,0,0,0.28)]">
      <div className="flex items-center gap-4">
        <span className={`grid h-14 w-14 shrink-0 place-items-center rounded-full bg-gradient-to-br ${tone} text-white shadow-[0_16px_36px_rgba(124,58,237,0.2)]`}>
          <Icon size={25} />
        </span>
        <div>
          <p className="text-sm text-slate-300">{label}</p>
          <p className="mt-2 text-sm font-semibold text-white">Sem dados reais</p>
          <p className="mt-1 text-xs text-slate-500">{empty}</p>
        </div>
      </div>
    </article>
  );
}

function RevenueInvestmentCard() {
  return (
    <section className="rounded-2xl border border-white/10 bg-slate-950/60 p-5 shadow-[0_20px_60px_rgba(0,0,0,0.24)]">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-display text-xl text-white">Receita x Investimento</h2>
        <button className="inline-flex items-center gap-2 rounded-lg border border-white/10 px-3 py-2 text-xs text-slate-300" type="button">
          Diario <ChevronDown size={13} />
        </button>
      </div>
      <div className="relative h-52 rounded-2xl border border-white/10 bg-white/[0.025] p-4">
        <div className="absolute inset-x-4 top-8 h-px bg-white/10" />
        <div className="absolute inset-x-4 top-20 h-px bg-white/10" />
        <div className="absolute inset-x-4 top-32 h-px bg-white/10" />
        <div className="absolute inset-x-4 bottom-9 h-px bg-white/10" />
        <EmptyPanel min="min-h-full">Sem serie temporal real. Conecte campanhas e Revenue para exibir receita e investimento.</EmptyPanel>
      </div>
    </section>
  );
}

function ChannelsCard() {
  const channels = ['Instagram', 'WhatsApp', 'Google Ads', 'Website', 'Meta Ads', 'Outros'];
  return (
    <section className="rounded-2xl border border-white/10 bg-slate-950/60 p-5 shadow-[0_20px_60px_rgba(0,0,0,0.24)]">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-display text-xl text-white">Canais que mais geram receita</h2>
        <button className="inline-flex items-center gap-2 rounded-lg border border-white/10 px-3 py-2 text-xs text-slate-300" type="button">
          Periodo <ChevronDown size={13} />
        </button>
      </div>
      <div className="grid gap-5 md:grid-cols-[190px_1fr] md:items-center">
        <div className="mx-auto grid h-40 w-40 place-items-center rounded-full bg-[conic-gradient(rgba(148,163,184,0.18)_0deg,rgba(148,163,184,0.18)_360deg)]">
          <div className="grid h-24 w-24 place-items-center rounded-full bg-slate-950 text-center">
            <p className="text-xs text-slate-400">Sem dados</p>
          </div>
        </div>
        <div className="space-y-2">
          {channels.map((channel) => (
            <div key={channel} className="grid grid-cols-[1fr_auto] items-center gap-3 rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2 text-sm">
              <span className="text-slate-300">{channel}</span>
              <span className="text-slate-500">Pendente</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function FunnelCard() {
  const stages = ['Impressoes', 'Cliques', 'Leads', 'Reservas', 'Receita'];
  return (
    <section className="rounded-2xl border border-white/10 bg-slate-950/60 p-5 shadow-[0_20px_60px_rgba(0,0,0,0.24)]">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-display text-xl text-white">Funil de conversao</h2>
        <button className="inline-flex items-center gap-2 rounded-lg border border-white/10 px-3 py-2 text-xs text-slate-300" type="button">
          Periodo <ChevronDown size={13} />
        </button>
      </div>
      <div className="grid gap-4 md:grid-cols-[170px_1fr]">
        <div className="flex flex-col items-center justify-center gap-1">
          {['w-36 bg-violet-600/40', 'w-30 bg-blue-600/35', 'w-24 bg-cyan-600/35', 'w-18 bg-emerald-600/35', 'w-12 bg-amber-500/35'].map((cls, idx) => (
            <div key={stages[idx]} className={`${cls} h-8 rounded-sm`} />
          ))}
        </div>
        <div className="space-y-2">
          {stages.map((stage) => (
            <div key={stage} className="grid grid-cols-[1fr_auto] rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2 text-sm">
              <span className="text-slate-300">{stage}</span>
              <span className="text-slate-500">Sem dados</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function ActionPlanCard() {
  return (
    <section className="rounded-2xl border border-white/10 bg-slate-950/60 p-5 shadow-[0_20px_60px_rgba(0,0,0,0.24)]">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <h2 className="font-display text-xl text-white">Plano de Acao</h2>
        <div className="flex gap-2">
          <button type="button" className="inline-flex items-center gap-2 rounded-lg bg-violet-600 px-3 py-2 text-xs font-semibold text-white">
            <Plus size={14} /> Novo Plano
          </button>
          <button type="button" className="rounded-lg border border-white/10 px-3 py-2 text-xs text-slate-300">Importar do Revenue</button>
        </div>
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        {actionColumns.map((column) => (
          <div key={column.title} className={`rounded-2xl border border-white/10 bg-gradient-to-b ${column.tone} p-3`}>
            <div className="mb-3 flex items-center justify-between">
              <p className="font-semibold text-white">{column.title}</p>
              <span className="rounded-full bg-white/10 px-2 py-0.5 text-xs text-slate-300">0</span>
            </div>
            <EmptyPanel min="min-h-44">Nenhum plano real nesta etapa.</EmptyPanel>
          </div>
        ))}
      </div>
    </section>
  );
}

function CampaignsCard({ projects }: { projects: MarketingProject[] }) {
  return (
    <section className="rounded-2xl border border-white/10 bg-slate-950/60 p-5 shadow-[0_20px_60px_rgba(0,0,0,0.24)]">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-display text-xl text-white">Campanhas</h2>
        <span className="rounded-lg border border-white/10 px-3 py-2 text-xs text-slate-300">{projects.length} reais</span>
      </div>
      {projects.length === 0 ? (
        <EmptyPanel>Nenhuma campanha real encontrada. Crie um projeto de marketing ou conecte uma integracao.</EmptyPanel>
      ) : (
        <div className="space-y-2">
          {projects.map((project) => (
            <Link key={project.id} to={`/app/marketing/projects/${project.id}`} className="grid gap-2 rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm transition hover:border-violet-300/40 md:grid-cols-[1fr_auto] md:items-center">
              <div className="flex items-center gap-3">
                <Instagram size={18} className="text-pink-300" />
                <div>
                  <p className="font-semibold text-white">{project.name}</p>
                  <p className="text-xs text-slate-400">{project.objective}</p>
                </div>
              </div>
              <span className="rounded-full border border-blue-300/20 bg-blue-400/10 px-3 py-1 text-xs text-blue-200">Projeto real</span>
            </Link>
          ))}
        </div>
      )}
    </section>
  );
}

function PlanDetailsCard({ selected }: { selected: MarketingProject | null }) {
  return (
    <section className="rounded-2xl border border-white/10 bg-slate-950/60 p-5 shadow-[0_20px_60px_rgba(0,0,0,0.24)]">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-display text-xl text-white">Detalhes do Plano</h2>
        <MoreVertical size={17} className="text-slate-500" />
      </div>
      {selected ? (
        <div className="space-y-4 text-sm">
          <div>
            <p className="text-xs text-slate-500">Nome</p>
            <p className="font-semibold text-white">{selected.name}</p>
          </div>
          <div>
            <p className="text-xs text-slate-500">Objetivo</p>
            <p className="text-slate-200">{selected.objective}</p>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
              <p className="text-xs text-slate-500">Publico</p>
              <p className="text-slate-200">{selected.audience}</p>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/[0.03] p-3">
              <p className="text-xs text-slate-500">Oferta</p>
              <p className="text-slate-200">{selected.offer}</p>
            </div>
          </div>
          <Link to={`/app/marketing/projects/${selected.id}`} className="flex items-center justify-between rounded-xl border border-violet-300/30 bg-violet-500/10 px-4 py-3 text-sm font-semibold text-violet-100">
            Ver detalhes <CheckCircle2 size={16} />
          </Link>
        </div>
      ) : (
        <EmptyPanel min="min-h-56">Selecione uma campanha real para exibir detalhes do plano.</EmptyPanel>
      )}
    </section>
  );
}

function CalendarCard() {
  const days = ['SEG 24', 'TER 25', 'QUA 26', 'QUI 27', 'SEX 28', 'SAB 29', 'DOM 30'];
  return (
    <section className="rounded-2xl border border-white/10 bg-slate-950/60 p-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-display text-xl text-white">Calendario</h2>
        <button type="button" className="rounded-lg border border-white/10 px-3 py-2 text-xs text-slate-300">Ver calendario</button>
      </div>
      <div className="grid grid-cols-7 gap-2">
        {days.map((day) => (
          <div key={day} className="min-h-24 rounded-xl border border-white/10 bg-white/[0.025] p-2">
            <p className="text-[0.68rem] font-semibold text-slate-400">{day}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

function ContentCard() {
  return (
    <section className="rounded-2xl border border-white/10 bg-slate-950/60 p-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-display text-xl text-white">Conteudo</h2>
        <Link to="/app/studio" className="rounded-lg border border-white/10 px-3 py-2 text-xs text-slate-300">Criar no Studio</Link>
      </div>
      <EmptyPanel min="min-h-28">Nenhum conteudo real associado a campanhas.</EmptyPanel>
    </section>
  );
}

function CompactListCard({ title, icon: Icon, items }: { title: string; icon: LucideIcon; items: string[] }) {
  return (
    <section className="rounded-2xl border border-white/10 bg-slate-950/60 p-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-display text-xl text-white">{title}</h2>
        <Icon size={19} className="text-slate-400" />
      </div>
      <div className="space-y-2">
        {items.map((item) => (
          <div key={item} className="rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2 text-sm text-slate-300">{item}</div>
        ))}
      </div>
    </section>
  );
}

function RightRail() {
  return (
    <aside className="space-y-5">
      <section className="rounded-2xl border border-violet-300/20 bg-[radial-gradient(circle_at_15%_0%,rgba(124,58,237,0.24),transparent_38%),linear-gradient(145deg,rgba(15,23,42,0.94),rgba(2,6,23,0.78))] p-5 shadow-[0_20px_60px_rgba(76,29,149,0.22)]">
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="grid h-11 w-11 place-items-center rounded-full bg-violet-500/20 text-violet-100">
              <Wand2 size={21} />
            </span>
            <h2 className="font-display text-xl text-white">Insights IA</h2>
          </div>
          <MoreVertical size={17} className="text-slate-500" />
        </div>
        <EmptyPanel min="min-h-52">Sem dados suficientes para gerar insights confiaveis. Conecte Revenue e canais reais.</EmptyPanel>
        <button type="button" className="mt-4 w-full rounded-xl bg-violet-600 px-4 py-3 text-sm font-semibold text-white disabled:opacity-50" disabled>
          Criar Plano
        </button>
      </section>

      <section className="rounded-2xl border border-white/10 bg-slate-950/60 p-5">
        <h2 className="font-display text-xl text-white">Proximas acoes</h2>
        <EmptyPanel min="mt-4 min-h-32">Nenhuma tarefa real criada.</EmptyPanel>
      </section>

      <section className="rounded-2xl border border-white/10 bg-slate-950/60 p-5">
        <h2 className="font-display text-xl text-white">Atividades recentes</h2>
        <EmptyPanel min="mt-4 min-h-32">Nenhuma atividade real registrada.</EmptyPanel>
      </section>
    </aside>
  );
}

export function MarketingProjectsPage() {
  const [projects, setProjects] = useState<MarketingProject[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchParams, setSearchParams] = useSearchParams();
  const currentView = (searchParams.get('view') ?? 'overview') as MarketingView;
  const selectedProject = projects[0] ?? null;

  useEffect(() => {
    setLoading(true);
    listProjects()
      .then((rows) => {
        setProjects(Array.isArray(rows) ? rows : []);
        setError(null);
      })
      .catch((err) => {
        setError(err instanceof Error ? err.message : 'Erro ao carregar Marketing');
        setProjects([]);
      })
      .finally(() => setLoading(false));
  }, []);

  const visibleProjects = useMemo(() => projects.slice(0, 6), [projects]);

  function selectView(view: MarketingView) {
    const next = new URLSearchParams(searchParams);
    next.set('view', view);
    setSearchParams(next, { replace: true });
  }

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 size={24} className="animate-spin text-cyan" />
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-2rem)] rounded-[1.75rem] border border-white/10 bg-[radial-gradient(circle_at_8%_0%,rgba(124,58,237,0.14),transparent_30%),#050914] p-5 text-white shadow-[0_28px_100px_rgba(0,0,0,0.48)] md:p-7">
      <header className="flex flex-col gap-5 xl:flex-row xl:items-start xl:justify-between">
        <div>
          <h1 className="font-display text-4xl text-white">Marketing</h1>
          <p className="mt-1 text-sm text-slate-300">Planeje, execute e acompanhe campanhas e acoes.</p>
        </div>
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
          <label className="flex min-w-[320px] items-center gap-3 rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm text-slate-400">
            <Search size={17} />
            <span>Buscar campanhas, planos, conteudos...</span>
          </label>
          <button type="button" className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-slate-950/70 px-4 py-3 text-sm font-semibold text-white">
            <CalendarDays size={16} /> 24 Mai - 23 Jun 2026 <ChevronDown size={14} />
          </button>
          <button type="button" className="hidden h-11 w-11 items-center justify-center rounded-full border border-white/10 text-slate-300 lg:inline-flex" aria-label="Notificacoes">
            <Bell size={18} />
          </button>
          <button type="button" className="hidden h-11 w-11 items-center justify-center rounded-full border border-white/10 text-slate-300 lg:inline-flex" aria-label="Ajuda">
            <HelpCircle size={18} />
          </button>
        </div>
      </header>

      <nav className="mt-6 flex gap-2 overflow-x-auto border-b border-white/10 pb-0">
        {marketingViews.map((view) => (
          <button
            key={view.key}
            type="button"
            onClick={() => selectView(view.key)}
            className={[
              'shrink-0 border-b-2 px-2 pb-3 text-sm font-semibold transition',
              currentView === view.key ? 'border-violet-400 text-violet-200' : 'border-transparent text-slate-400 hover:text-white',
            ].join(' ')}
          >
            {view.label}
          </button>
        ))}
      </nav>

      {error ? <div className="mt-5 rounded-2xl border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-100">{error}</div> : null}

      <section className="mt-5 grid gap-5 md:grid-cols-2 2xl:grid-cols-5">
        {kpiCards.map((card) => <KpiCard key={card.label} {...card} />)}
      </section>

      <div className="mt-5 grid gap-5 2xl:grid-cols-[minmax(0,1fr)_340px]">
        <main className="space-y-5">
          <section className="grid gap-5 xl:grid-cols-[1.1fr_0.9fr_0.9fr]">
            <RevenueInvestmentCard />
            <ChannelsCard />
            <FunnelCard />
          </section>

          <section className="grid gap-5 xl:grid-cols-[1.2fr_0.8fr_0.8fr]">
            <ActionPlanCard />
            <CampaignsCard projects={visibleProjects} />
            <PlanDetailsCard selected={selectedProject} />
          </section>

          <section className="grid gap-5 xl:grid-cols-3">
            <CalendarCard />
            <ContentCard />
            <CompactListCard title="Audiencias" icon={Users} items={['Sem audiencias reais importadas do Revenue.']} />
          </section>

          <section className="grid gap-5 xl:grid-cols-3">
            <CompactListCard title="Automacoes" icon={Bot} items={['Sem automacoes reais configuradas.']} />
            <CompactListCard title="Relatorios" icon={FileText} items={['Exportar PDF indisponivel sem dados reais.', 'Exportar Excel indisponivel sem dados reais.', 'Enviar por Email indisponivel sem dados reais.', 'Conectar Power BI em Integrations.']} />
            <CompactListCard title="Portas de integracao" icon={FileSpreadsheet} items={['Meta Ads', 'Instagram Graph API', 'Google Ads', 'WhatsApp Business API']} />
          </section>
        </main>
        <RightRail />
      </div>
    </div>
  );
}
