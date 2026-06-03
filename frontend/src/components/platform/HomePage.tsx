import { BadgeDollarSign, Bot, Link2, Megaphone, MessageSquare, Sparkles, type LucideIcon } from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';

import { getChatSummary } from '../../services/chats.service';
import { getMarketingOverview } from '../../services/marketing.service';
import { getRevenueIntelligence } from '../../services/revenue.service';
import { getStudioOverview } from '../../services/studio.service';

type ModuleKey = 'revenue' | 'chats' | 'assistant' | 'marketing' | 'studio' | 'integrations';

interface ModuleCardState {
  status: 'online' | 'unavailable' | 'manual';
  quantity: string;
  lastActivity: string;
  error?: string;
}

interface HomeModule {
  key: ModuleKey;
  title: string;
  description: string;
  to: string;
  icon: LucideIcon;
  tone: string;
}

const modules: HomeModule[] = [
  {
    key: 'revenue',
    title: 'Revenue',
    description: 'Central de inteligencia, funil, reservas e ROI.',
    to: '/app/revenue?view=business-pulse',
    icon: BadgeDollarSign,
    tone: 'from-emerald-400/24 to-cyan-400/10 text-emerald-200',
  },
  {
    key: 'chats',
    title: 'Chats',
    description: 'Atendimento omnichannel e alternancia IA humano.',
    to: '/app/chats',
    icon: MessageSquare,
    tone: 'from-blue-400/24 to-violet-400/10 text-blue-200',
  },
  {
    key: 'assistant',
    title: 'AXI Assistant',
    description: 'Analises, planos e recomendacoes conectadas aos dados.',
    to: '/app/assistant',
    icon: Bot,
    tone: 'from-violet-400/28 to-fuchsia-400/10 text-violet-200',
  },
  {
    key: 'marketing',
    title: 'Marketing',
    description: 'Planejamento, campanhas, audiencias e relatorios.',
    to: '/app/marketing',
    icon: Megaphone,
    tone: 'from-amber-400/24 to-rose-400/10 text-amber-200',
  },
  {
    key: 'studio',
    title: 'Studio',
    description: 'Criacao visual, templates, uploads e editor.',
    to: '/app/studio',
    icon: Sparkles,
    tone: 'from-cyan-400/20 to-violet-400/14 text-cyan-200',
  },
  {
    key: 'integrations',
    title: 'Integrations',
    description: 'Canais, provedores e plataformas conectadas.',
    to: '/app/integrations',
    icon: Link2,
    tone: 'from-slate-300/16 to-blue-400/10 text-slate-200',
  },
];

const initialState: Record<ModuleKey, ModuleCardState> = {
  revenue: { status: 'manual', quantity: 'Aguardando dados', lastActivity: 'Validando Revenue' },
  chats: { status: 'manual', quantity: 'Aguardando dados', lastActivity: 'Validando conversas' },
  assistant: { status: 'manual', quantity: 'Conectado ao chat', lastActivity: 'Usa os dados reais disponiveis' },
  marketing: { status: 'manual', quantity: 'Aguardando dados', lastActivity: 'Validando campanhas' },
  studio: { status: 'manual', quantity: 'Aguardando dados', lastActivity: 'Validando projetos' },
  integrations: { status: 'manual', quantity: 'Configuracao manual', lastActivity: 'Abra para verificar conexoes' },
};

function errorMessage(reason: unknown) {
  return reason instanceof Error ? reason.message : 'Servico indisponivel no momento.';
}

function statusLabel(status: ModuleCardState['status']) {
  if (status === 'online') return 'Operacional';
  if (status === 'unavailable') return 'Indisponivel';
  return 'Verificar';
}

function statusClass(status: ModuleCardState['status']) {
  if (status === 'online') return 'border-emerald-400/25 bg-emerald-500/12 text-emerald-300';
  if (status === 'unavailable') return 'border-rose-400/25 bg-rose-500/12 text-rose-200';
  return 'border-amber-400/25 bg-amber-500/12 text-amber-200';
}

function readRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? value as Record<string, unknown> : {};
}

export function HomePage() {
  const [moduleState, setModuleState] = useState<Record<ModuleKey, ModuleCardState>>(initialState);

  useEffect(() => {
    let mounted = true;

    async function load() {
      const [revenue, chats, marketing, studio] = await Promise.allSettled([
        getRevenueIntelligence(30),
        getChatSummary(),
        getMarketingOverview(),
        getStudioOverview(),
      ]);

      if (!mounted) return;

      setModuleState((current) => {
        const next = { ...current };

        if (revenue.status === 'fulfilled') {
          next.revenue = {
            status: 'online',
            quantity: `${revenue.value.summary.reservas_fechadas} reservas`,
            lastActivity: `Receita real: ${new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(revenue.value.summary.receita_total)}`,
          };
        } else {
          next.revenue = { status: 'unavailable', quantity: 'Erro ao carregar', lastActivity: 'Revenue nao respondeu', error: errorMessage(revenue.reason) };
        }

        if (chats.status === 'fulfilled') {
          const data = readRecord(chats.value);
          const total = Number(data.open_conversations ?? data.total_conversations ?? data.conversations ?? 0);
          next.chats = { status: 'online', quantity: `${total} conversas`, lastActivity: 'Resumo carregado do backend' };
        } else {
          next.chats = { status: 'unavailable', quantity: 'Erro ao carregar', lastActivity: 'Chats nao respondeu', error: errorMessage(chats.reason) };
        }

        if (marketing.status === 'fulfilled') {
          const data = readRecord(marketing.value);
          const total = Number(data.active_campaigns ?? data.campaigns_count ?? data.total_campaigns ?? 0);
          next.marketing = { status: 'online', quantity: `${total} campanhas`, lastActivity: 'Overview carregado do backend' };
        } else {
          next.marketing = { status: 'unavailable', quantity: 'Erro ao carregar', lastActivity: 'Marketing nao respondeu', error: errorMessage(marketing.reason) };
        }

        if (studio.status === 'fulfilled') {
          const data = readRecord(studio.value);
          const total = Number(data.projects_count ?? data.total_projects ?? data.recent_projects_count ?? 0);
          next.studio = { status: 'online', quantity: `${total} projetos`, lastActivity: 'Overview carregado do backend' };
        } else {
          next.studio = { status: 'unavailable', quantity: 'Erro ao carregar', lastActivity: 'Studio nao respondeu', error: errorMessage(studio.reason) };
        }

        return next;
      });
    }

    void load();
    return () => {
      mounted = false;
    };
  }, []);

  const operationalCount = useMemo(() => Object.values(moduleState).filter((item) => item.status === 'online').length, [moduleState]);

  return (
    <div className="space-y-6 text-white">
      <header className="rounded-[1.75rem] border border-white/10 bg-[radial-gradient(circle_at_12%_0%,rgba(124,58,237,0.24),transparent_34%),linear-gradient(145deg,rgba(15,23,42,0.92),rgba(2,6,23,0.78))] p-6 shadow-[0_26px_90px_rgba(0,0,0,0.36)] md:p-7">
        <p className="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-200">AXI Platform</p>
        <h1 className="mt-3 font-display text-4xl">Home</h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-300">
          Entrada oficial da plataforma. Abra cada modulo a partir daqui sem duplicar dashboards ou criar rotas paralelas.
        </p>
        <div className="mt-5 inline-flex rounded-full border border-white/10 bg-white/[0.04] px-4 py-2 text-sm text-slate-300">
          {operationalCount} de {modules.length - 2} modulos com dados carregados nesta sessao
        </div>
      </header>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {modules.map((module) => {
          const state = moduleState[module.key];
          const Icon = module.icon;
          return (
            <article key={module.key} className="flex min-h-[240px] flex-col rounded-2xl border border-white/10 bg-[linear-gradient(145deg,rgba(15,23,42,0.86),rgba(2,6,23,0.68))] p-5 shadow-[0_18px_70px_rgba(0,0,0,0.28)]">
              <div className="flex items-start justify-between gap-4">
                <span className={`grid h-14 w-14 place-items-center rounded-2xl bg-gradient-to-br ${module.tone}`}>
                  <Icon size={25} />
                </span>
                <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${statusClass(state.status)}`}>{statusLabel(state.status)}</span>
              </div>
              <h2 className="mt-5 font-display text-2xl">{module.title}</h2>
              <p className="mt-2 min-h-11 text-sm leading-6 text-slate-400">{module.description}</p>
              <div className="mt-5 rounded-2xl border border-white/10 bg-white/[0.035] p-4">
                <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Quantidade</p>
                <p className="mt-1 text-lg font-semibold text-white">{state.quantity}</p>
                <p className="mt-3 text-xs uppercase tracking-[0.18em] text-slate-500">Ultima atividade</p>
                <p className="mt-1 text-sm text-slate-300">{state.lastActivity}</p>
                {state.error ? <p className="mt-3 text-xs text-rose-200">{state.error}</p> : null}
              </div>
              <Link to={module.to} className="mt-auto inline-flex h-11 items-center justify-center rounded-xl bg-violet-600 px-4 text-sm font-semibold text-white transition hover:bg-violet-500">
                Abrir
              </Link>
            </article>
          );
        })}
      </section>
    </div>
  );
}
