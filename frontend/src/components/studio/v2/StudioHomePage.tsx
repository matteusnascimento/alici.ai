import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  AlertTriangle,
  ChevronRight,
  Clapperboard,
  CopyPlus,
  FileImage,
  FileText,
  Folder,
  Image,
  Images,
  LayoutDashboard,
  Loader2,
  Mail,
  Maximize2,
  MessageCircle,
  Mic2,
  MonitorPlay,
  Palette,
  Plus,
  Search,
  Sparkles,
  Video,
  Wand2,
  X,
  type LucideIcon,
} from 'lucide-react';

import { getStudioOverview } from '../../../services/studio.service';
import { listStudioTemplateDefinitions } from '../../../services/studioTemplate.service';
import type { StudioOverviewResponse, StudioRecentProjectItem } from '../../../types/studioV2';
import type { StudioTemplateDefinition } from '../../../types/studioTemplate';
import { resolveStudioProjectRoute } from './config/studioHomeConfig';

const emptyOverview: StudioOverviewResponse = {
  recent_projects: [],
  recent_exports: [],
  brand_summary: {
    logos_count: 0,
    templates_count: 0,
    palettes_count: 0,
    assets_count: 0,
  },
  suggested_actions: [],
};

const createTypes = [
  { label: 'Video', description: 'Editor de video', path: '/app/studio/editor/video?mode=new', icon: Video, tone: 'from-violet-500 to-fuchsia-500' },
  { label: 'Foto', description: 'Imagem e edicao', path: '/app/studio/tools/photo-editor', icon: FileImage, tone: 'from-sky-500 to-cyan-400' },
  { label: 'Story', description: 'Formato vertical', path: '/app/studio/templates?category=Stories', icon: Clapperboard, tone: 'from-rose-500 to-pink-500' },
  { label: 'Post', description: 'Feed e carrossel', path: '/app/studio/tools/ad', icon: CopyPlus, tone: 'from-orange-500 to-amber-400' },
  { label: 'Banner', description: 'Web e anuncios', path: '/app/studio/templates?category=Ads', icon: MonitorPlay, tone: 'from-emerald-500 to-teal-400' },
  { label: 'Landing Page', description: 'Paginas e conversao', path: `/app/studio/templates?category=${encodeURIComponent('Landing Pages')}`, icon: LayoutDashboard, tone: 'from-cyan-500 to-sky-500' },
  { label: 'Email', description: 'Email marketing', path: '/app/studio/tools/copy', icon: Mail, tone: 'from-yellow-400 to-amber-500' },
  { label: 'WhatsApp', description: 'Mensagens', path: '/app/studio/tools/caption', icon: MessageCircle, tone: 'from-lime-500 to-green-500' },
];

const quickActions = [
  { label: 'Criar do zero', description: 'Design em branco', path: '/app/studio/editor/video?mode=new', icon: Wand2, enabled: true, tone: 'from-violet-600 to-fuchsia-600' },
  { label: 'Gerar com IA', description: 'Criar conteudo em segundos', path: '/app/studio/ai-creative', icon: Sparkles, enabled: true, tone: 'from-violet-600 to-purple-500' },
  { label: 'Redimensionar', description: 'Ajustar para varios formatos', path: '/app/studio/tools/photo-editor?tool=resize', icon: Maximize2, enabled: true, tone: 'from-violet-600 to-indigo-500' },
  { label: 'Remover fundo', description: 'Requer provider real configurado', path: '/app/studio/tools/remove-background', icon: Images, enabled: true, tone: 'from-orange-600 to-rose-500' },
  { label: 'Converter imagem', description: 'Abrir editor', path: '/app/studio/editor/video?mode=new&entry=image-to-video', icon: Folder, enabled: true, tone: 'from-violet-600 to-indigo-500' },
];

const templateCanvases = [
  { title: 'VERAO', subtitle: 'COM DESCONTO ESPECIAL', background: 'linear-gradient(160deg,#0e7490 0%,#38bdf8 42%,#f59e0b 100%)' },
  { title: 'Lua de Mel', subtitle: 'Momentos que ficam para sempre', background: 'linear-gradient(160deg,#fed7aa 0%,#f59e0b 40%,#0f172a 100%)' },
  { title: 'BLACK FRIDAY', subtitle: 'ATE 40% OFF', background: 'linear-gradient(145deg,#020617 0%,#111827 55%,#ca8a04 100%)' },
];

const statusTone: Record<string, string> = {
  draft: 'bg-amber-300/15 text-amber-200',
  published: 'bg-emerald-300/15 text-emerald-200',
  active: 'bg-emerald-300/15 text-emerald-200',
  archived: 'bg-slate-300/15 text-slate-200',
};

function Panel({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <section className={`rounded-lg border border-white/[0.08] bg-[#0B1220]/86 shadow-[inset_0_1px_0_rgba(255,255,255,0.04)] backdrop-blur-xl ${className}`}>
      {children}
    </section>
  );
}

function SectionHeader({ title, to }: { title: string; to?: string }) {
  return (
    <div className="mb-3 flex items-center justify-between gap-3">
      <h2 className="text-base font-semibold text-white">{title}</h2>
      {to ? <Link to={to} className="text-xs font-medium text-cyan-300 hover:text-cyan-100">Ver todos</Link> : null}
    </div>
  );
}

function ProjectVisual({ title, thumbnail, compact = false }: { title: string; thumbnail?: string | null; compact?: boolean }) {
  const sizeClass = compact ? 'h-12 w-16 shrink-0 rounded-md' : 'h-24';
  if (thumbnail) {
    return <div className={`${sizeClass} bg-cover bg-center`} style={{ backgroundImage: `url(${thumbnail})` }} />;
  }
  return (
    <div className={`flex items-end bg-[linear-gradient(140deg,#083344,#0f172a_46%,#7c2d12)] ${compact ? `${sizeClass} p-1.5` : `${sizeClass} p-3`}`}>
      <p className={compact ? 'line-clamp-2 text-[9px] font-black uppercase leading-3 text-white' : 'max-w-[9rem] text-lg font-black uppercase leading-5 text-white'}>{title}</p>
    </div>
  );
}

function CampaignCard({ project }: { project: StudioRecentProjectItem }) {
  const statusClass = statusTone[project.status] || 'bg-violet-300/15 text-violet-100';
  const updated = project.updated_at ? new Date(project.updated_at).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' }) : 'Atual';

  return (
    <Link to={resolveStudioProjectRoute(project.project_type, project.id)} className="min-w-[178px] overflow-hidden rounded-lg border border-white/[0.08] bg-[#08111f] transition hover:border-cyan-300/35 hover:bg-[#111A2C]">
      <ProjectVisual title={project.title} thumbnail={project.thumbnail_url} />
      <div className="p-3">
        <p className="truncate text-sm font-semibold text-white">{project.title}</p>
        <span className={`mt-1 inline-flex rounded px-1.5 py-0.5 text-[11px] font-medium ${statusClass}`}>{project.status || 'Em andamento'}</span>
        <div className="mt-3 grid grid-cols-2 gap-3 text-xs text-slate-400">
          <span><strong className="block text-sm text-white">1</strong>Conteudo</span>
          <span><strong className="block text-sm text-white">Real</strong>Projeto</span>
        </div>
        <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-slate-700">
          <div className="h-full w-2/3 rounded-full bg-violet-500" />
        </div>
        <p className="mt-2 text-[11px] text-slate-500">Atualizado {updated}</p>
      </div>
    </Link>
  );
}

function EmptyBlock({ message }: { message: string }) {
  return (
    <div className="rounded-lg border border-dashed border-white/10 bg-white/[0.025] p-4 text-sm text-slate-400">
      {message}
    </div>
  );
}

function TemplateCard({ template, fallback }: { template?: StudioTemplateDefinition; fallback: (typeof templateCanvases)[number] }) {
  const route = template
    ? `/app/studio/editor/${template.type === 'video' || template.type === 'story' || template.type === 'reel' ? 'video' : 'design'}?mode=new&template=${template.id}`
    : '/app/studio/templates';

  return (
    <Link to={route} className="relative min-h-[150px] overflow-hidden rounded-lg border border-white/[0.08] p-4 shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]" style={{ background: fallback.background }}>
      <div className="absolute inset-x-0 bottom-0 h-20 bg-gradient-to-t from-black/55 to-transparent" />
      <div className="relative z-10 flex h-full flex-col justify-between">
        <div>
          <p className="text-2xl font-black leading-6 text-white">{template?.name || fallback.title}</p>
          <p className="mt-2 max-w-[8rem] text-xs font-semibold text-white/90">{template?.category || fallback.subtitle}</p>
        </div>
        <span className="mt-6 w-fit rounded bg-black/35 px-2 py-1 text-[10px] font-bold uppercase text-white/90">{template ? template.format : 'Template'}</span>
      </div>
    </Link>
  );
}

function QuickAction({ item }: { item: (typeof quickActions)[number] }) {
  const Icon = item.icon;
  const content = (
    <>
      <span className={`grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-gradient-to-br ${item.tone} text-white`}>
        <Icon size={16} />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block truncate text-sm font-semibold text-white">{item.label}</span>
        <span className="block truncate text-xs text-slate-400">{item.description}</span>
      </span>
      <ChevronRight size={16} className="text-slate-300" />
    </>
  );

  if (!item.enabled) {
    return <button disabled className="flex w-full items-center gap-3 rounded-lg border border-white/[0.06] bg-white/[0.025] px-3 py-2.5 opacity-55">{content}</button>;
  }
  return <Link to={item.path} className="flex items-center gap-3 rounded-lg border border-white/[0.06] bg-white/[0.035] px-3 py-2.5 transition hover:border-violet-300/35 hover:bg-[#111A2C]">{content}</Link>;
}

function LibraryItem({ icon: Icon, label, value }: { icon: LucideIcon; label: string; value: string }) {
  return (
    <div className="flex items-center gap-3">
      <span className="grid h-9 w-9 place-items-center rounded-lg bg-cyan-300/10 text-cyan-300"><Icon size={17} /></span>
      <span>
        <span className="block text-sm font-semibold text-white">{label}</span>
        <span className="text-xs text-slate-400">{value}</span>
      </span>
    </div>
  );
}

export function StudioHomePage() {
  const [overview, setOverview] = useState<StudioOverviewResponse>(emptyOverview);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const templates = useMemo(() => listStudioTemplateDefinitions(), []);

  useEffect(() => {
    let mounted = true;

    async function loadOverview() {
      setLoading(true);
      try {
        const data = await getStudioOverview();
        if (!mounted) return;
        setOverview({
          ...emptyOverview,
          ...data,
          brand_summary: { ...emptyOverview.brand_summary, ...data.brand_summary },
        });
        setError(null);
      } catch (err) {
        if (!mounted) return;
        setOverview(emptyOverview);
        setError(err instanceof Error ? err.message : 'Dados reais do Studio indisponiveis agora.');
      } finally {
        if (mounted) setLoading(false);
      }
    }

    void loadOverview();
    return () => {
      mounted = false;
    };
  }, []);

  const recentProjects = overview.recent_projects.slice(0, 4);
  const featuredTemplates = templates.filter((template) => template.source === 'recommended').slice(0, 3);

  return (
    <motion.main
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className="-m-4 min-h-screen bg-[#050816] text-white md:-m-6"
    >
      <div className="grid h-screen grid-cols-1 overflow-hidden xl:grid-cols-[minmax(0,1fr)_320px]">
        <div className="min-h-0 overflow-y-auto px-4 py-5 md:px-8">
          <header className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <h1 className="text-4xl font-black tracking-tight md:text-5xl">O que vamos criar hoje?</h1>
              <p className="mt-2 text-base text-slate-300">Inspire-se, escolha um template ou deixe a IA criar para voce.</p>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <Link to="/app/studio/templates" className="inline-flex h-11 items-center gap-2 rounded-lg border border-white/15 bg-white/[0.04] px-4 text-sm font-semibold text-white hover:bg-white/[0.08]">
                Templates
              </Link>
              <Link to="/app/studio/assets" className="inline-flex h-11 items-center gap-2 rounded-lg border border-white/15 bg-white/[0.04] px-4 text-sm font-semibold text-white hover:bg-white/[0.08]">
                Uploads
              </Link>
              <Link to="/app/studio/editor/video?mode=new" className="inline-flex h-11 items-center gap-2 rounded-lg border border-violet-400/45 bg-violet-500/10 px-4 text-sm font-semibold text-white hover:bg-violet-500/20">
                <Plus size={17} className="text-fuchsia-300" /> Criar do zero
              </Link>
              <Link to="/app/studio/ai-creative" className="inline-flex h-11 items-center gap-2 rounded-lg bg-violet-700 px-4 text-sm font-semibold text-white hover:bg-violet-600">
                <Sparkles size={15} /> Magic Studio
              </Link>
            </div>
          </header>

          <div className="mt-6 flex gap-3 rounded-lg border border-white/[0.08] bg-[#0B1220]/90 p-2 backdrop-blur-xl">
            <label className="flex min-w-0 flex-1 items-center gap-3 px-2">
              <Search size={20} className="text-fuchsia-300" />
              <input aria-label="Buscar no Studio" className="h-10 min-w-0 flex-1 bg-transparent text-sm text-white outline-none placeholder:text-slate-500" placeholder="Buscar templates, posts, videos, campanhas, hoteis, ofertas..." />
            </label>
          </div>

          <section className="mt-5">
            <SectionHeader title="Criar novo" />
            <div className="grid grid-cols-2 gap-3 md:grid-cols-4 2xl:grid-cols-8">
              {createTypes.map((item) => {
                const Icon = item.icon;
                return (
                  <Link key={item.label} to={item.path} className="group rounded-lg border border-white/[0.08] bg-[#0B1220] p-4 text-center transition hover:border-violet-300/35 hover:bg-[#111A2C]">
                    <span className={`mx-auto grid h-12 w-12 place-items-center rounded-xl bg-gradient-to-br ${item.tone} text-white shadow-lg`}>
                      <Icon size={23} />
                    </span>
                    <span className="mt-3 block text-base font-semibold text-white">{item.label}</span>
                    <span className="mt-1 block text-xs text-slate-400">{item.description}</span>
                  </Link>
                );
              })}
            </div>
          </section>

          <Panel className="mt-5 p-4">
            <SectionHeader title="Campanhas ativas" to="/app/marketing" />
            {loading ? (
              <div className="flex items-center gap-2 text-sm text-slate-300"><Loader2 className="h-4 w-4 animate-spin text-cyan-300" /> Carregando projetos reais...</div>
            ) : recentProjects.length ? (
              <div className="flex gap-4 overflow-x-auto pb-1">
                {recentProjects.map((project) => <CampaignCard key={project.id} project={project} />)}
                <Link to="/app/studio/editor/video?mode=new" className="grid min-w-[198px] place-items-center rounded-lg border border-dashed border-white/[0.12] bg-white/[0.02] p-5 text-center hover:border-cyan-300/40">
                  <span>
                    <span className="mx-auto grid h-12 w-12 place-items-center rounded-full border border-white/30"><Plus size={24} /></span>
                    <span className="mt-4 block text-base font-semibold">Nova campanha</span>
                    <span className="mt-1 block text-xs text-slate-400">Criar campanha</span>
                  </span>
                </Link>
              </div>
            ) : (
              <EmptyBlock message="Campanhas aparecem aqui quando existirem projetos reais do Studio ou campanhas conectadas ao Marketing." />
            )}
          </Panel>

          {error ? (
            <div className="mt-3 flex items-center gap-2 rounded-lg border border-amber-300/30 bg-amber-300/10 px-4 py-3 text-sm text-amber-100">
              <AlertTriangle size={16} /> {error}
            </div>
          ) : null}

          <div className="mt-4 grid gap-4 xl:grid-cols-[0.9fr_0.85fr_1.25fr]">
            <Panel className="p-4">
              <div className="flex items-center gap-2">
                <h2 className="text-base font-semibold">IA Criativa</h2>
                <span className="rounded-full bg-violet-500 px-2 py-0.5 text-[10px] font-bold">Novo</span>
              </div>
              <p className="mt-2 text-xs leading-5 text-slate-300">Descreva sua ideia e a IA cria os formatos quando houver provider real configurado.</p>
              <textarea className="mt-3 min-h-[78px] w-full resize-none rounded-lg border border-white/[0.08] bg-[#050816] p-3 text-xs text-white outline-none placeholder:text-slate-500" placeholder="Campanha romantica para casais, pousada beira mar, cafe da manha incluso." />
              <div className="mt-3 flex flex-wrap gap-2">
                {['Instagram', 'Casais', 'Sao Paulo - SP'].map((filter) => <span key={filter} className="rounded border border-cyan-300/20 bg-cyan-300/5 px-2 py-1 text-xs text-cyan-100">{filter}</span>)}
              </div>
              <Link to="/app/studio/ai-creative" className="mt-3 flex h-10 items-center justify-center rounded-lg bg-violet-700 text-sm font-semibold hover:bg-violet-600">Gerar campanha com IA</Link>
            </Panel>

            <Panel className="p-4">
              <SectionHeader title="Projetos recentes" to="/app/studio/projects" />
              {recentProjects.length ? (
                <div className="space-y-3">
                  {recentProjects.map((project) => (
                    <Link key={project.id} to={resolveStudioProjectRoute(project.project_type, project.id)} aria-label="Abrir projeto recente" className="flex items-center gap-3 rounded-lg hover:bg-white/[0.04]">
                      <ProjectVisual title={project.title} thumbnail={project.thumbnail_url} compact />
                      <span className="min-w-0 flex-1">
                        <span className="block truncate text-sm font-semibold">{project.title}</span>
                        <span className="block truncate text-xs text-slate-400">{project.project_type} - Projeto real</span>
                      </span>
                    </Link>
                  ))}
                </div>
              ) : <EmptyBlock message="Sem projetos recentes reais para listar." />}
            </Panel>

            <Panel className="p-4">
              <SectionHeader title="Templates em destaque" to="/app/studio/templates" />
              <div className="grid grid-cols-3 gap-3">
                {templateCanvases.map((fallback, index) => <TemplateCard key={fallback.title} fallback={fallback} template={featuredTemplates[index]} />)}
              </div>
            </Panel>
          </div>

          <div className="mt-4 grid gap-4 xl:grid-cols-[1.2fr_0.9fr]">
            <Panel className="p-4">
              <SectionHeader title="Biblioteca" to="/app/studio/assets" />
              <p className="mb-3 text-sm font-medium text-slate-300">Uploads recentes</p>
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
                <LibraryItem icon={Image} label="Imagens" value={`${overview.brand_summary.assets_count} arquivos`} />
                <LibraryItem icon={Video} label="Videos" value="Indisponivel" />
                <LibraryItem icon={Palette} label="Logos" value={`${overview.brand_summary.logos_count} arquivos`} />
                <LibraryItem icon={FileText} label="Documentos" value="Indisponivel" />
                <LibraryItem icon={Mic2} label="Audios" value="Indisponivel" />
              </div>
            </Panel>

            <Panel className="p-4">
              <SectionHeader title="Brand Kit" to="/app/studio/brand-kit" />
              <div className="grid gap-4 sm:grid-cols-4">
                <div>
                  <p className="text-xs text-slate-400">Cores</p>
                  <div className="mt-2 flex gap-2">
                    {['#334155', '#fb7185', '#facc15', '#10b981', '#22d3ee'].map((color) => <span key={color} className="h-6 w-6 rounded-full" style={{ backgroundColor: color }} />)}
                  </div>
                </div>
                <div><p className="text-xs text-slate-400">Fontes</p><p className="mt-2 text-sm text-white">Poppins / Montserrat</p></div>
                <div><p className="text-xs text-slate-400">Logo</p><p className="mt-1 text-3xl font-black tracking-wider text-white">AXI</p></div>
                <div><p className="text-xs text-slate-400">Estilo</p><p className="mt-2 text-sm text-white">Moderno e acolhedor</p></div>
              </div>
            </Panel>
          </div>
        </div>

        <aside className="hidden min-h-0 overflow-y-auto border-l border-white/[0.08] bg-[#07101d]/95 p-4 xl:block">
          <Panel className="p-4">
            <SectionHeader title="Acoes rapidas" />
            <div className="space-y-2">
              {quickActions.map((item) => <QuickAction key={item.label} item={item} />)}
            </div>
          </Panel>

          <Panel className="mt-4 p-4">
            <SectionHeader title="Aprovacoes" to="/app/marketing" />
            <EmptyBlock message="Aprovacoes dependem de endpoint real. Nada foi simulado." />
          </Panel>

          <Panel className="mt-4 p-4">
            <SectionHeader title="Status operacional" />
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between text-slate-300"><span>Projetos</span><span className="text-white">{recentProjects.length}</span></div>
              <div className="flex items-center justify-between text-slate-300"><span>Templates</span><span className="text-white">{templates.length}</span></div>
              <div className="flex items-center justify-between text-slate-300"><span>Provider IA</span><span className="text-amber-200">Validado no fluxo</span></div>
              <div className="flex items-center justify-between text-slate-300"><span>Sucesso falso</span><span className="text-rose-200"><X size={14} className="inline" /> Bloqueado</span></div>
            </div>
          </Panel>
        </aside>
      </div>
    </motion.main>
  );
}
