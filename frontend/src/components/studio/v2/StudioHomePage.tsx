import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  AlertTriangle,
  Bot,
  Clapperboard,
  Crown,
  FileImage,
  FolderOpen,
  ImageUp,
  LayoutTemplate,
  Loader2,
  Megaphone,
  Palette,
  Search,
  Sparkles,
  Trash2,
  Upload,
  Wand2,
} from 'lucide-react';

import { getStudioOverview } from '../../../services/studio.service';
import { listStudioTemplateDefinitions } from '../../../services/studioTemplate.service';
import type { StudioOverviewResponse } from '../../../types/studioV2';
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

const studioNav = [
  { label: 'Studio', path: '/app/studio', icon: Sparkles },
  { label: 'Templates', path: '/app/studio/templates', icon: LayoutTemplate },
  { label: 'Projetos', path: '/app/studio/projects', icon: FolderOpen },
  { label: 'Uploads', path: '/app/studio/assets', icon: ImageUp },
  { label: 'Brand Kit', path: '/app/studio/brand-kit', icon: Palette },
  { label: 'Magic Studio', path: '/app/studio/ai-creative', icon: Wand2 },
  { label: 'Lixeira', path: '/app/studio/projects?filter=trash', icon: Trash2 },
];

const createCards = [
  { label: 'Video', description: 'Editor com timeline compacta', path: '/app/studio/editor/video?mode=new', icon: Clapperboard },
  { label: 'Foto', description: 'Imagem, filtros e ajustes', path: '/app/studio/tools/photo-editor', icon: FileImage },
  { label: 'Story', description: 'Formato vertical para redes', path: '/app/studio/templates?category=Stories', icon: Sparkles },
  { label: 'Poster', description: 'Criativo para oferta ou evento', path: '/app/studio/tools/ad', icon: Megaphone },
  { label: 'Banner', description: 'Google Ads, site e campanhas', path: '/app/studio/templates?category=Ads', icon: LayoutTemplate },
  {
    label: 'Landing Page',
    description: 'Oferta, prova e conversao',
    path: `/app/studio/templates?category=${encodeURIComponent('Landing Pages')}`,
    icon: Bot,
  },
];

const templatePreview = [
  'linear-gradient(135deg,#2e1065,#c026d3 54%,#22d3ee)',
  'linear-gradient(135deg,#0f172a,#0891b2 52%,#a855f7)',
  'linear-gradient(135deg,#064e3b,#0891b2 52%,#f97316)',
  'linear-gradient(135deg,#08111f,#10b981 54%,#22d3ee)',
];

function templateRoute(template: StudioTemplateDefinition) {
  const target = template.type === 'video' || template.type === 'story' || template.type === 'reel' ? 'video' : 'design';
  return `/app/studio/editor/${target}?mode=new&template=${template.id}`;
}

function TemplateStrip({ title, templates }: { title: string; templates: StudioTemplateDefinition[] }) {
  return (
    <section>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="font-display text-2xl font-bold">{title}</h2>
        <Link to="/app/studio/templates" className="text-xs font-bold text-slate-300 hover:text-white">Ver todos</Link>
      </div>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        {templates.slice(0, 4).map((template, index) => (
          <Link key={template.id} to={templateRoute(template)} className="overflow-hidden rounded-2xl border border-white/10 bg-white/[0.055] hover:border-fuchsia-300/35">
            <div className="h-28" style={{ background: templatePreview[index % templatePreview.length] }} />
            <div className="p-3">
              <div className="flex items-center justify-between gap-2">
                <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-cyan-300">{template.category}</p>
                <span className={template.plan === 'premium' ? 'inline-flex items-center gap-1 rounded-full bg-fuchsia-300/15 px-2 py-0.5 text-[10px] font-bold text-fuchsia-100' : 'rounded-full bg-emerald-300/15 px-2 py-0.5 text-[10px] font-bold text-emerald-100'}>
                  {template.plan === 'premium' ? <Crown size={10} /> : null}
                  {template.plan === 'premium' ? 'Premium' : 'Free'}
                </span>
              </div>
              <p className="mt-1 font-bold">{template.name}</p>
              <p className="mt-1 text-xs text-slate-400">{template.format}</p>
            </div>
          </Link>
        ))}
      </div>
    </section>
  );
}

export function StudioHomePage() {
  const [overview, setOverview] = useState<StudioOverviewResponse>(emptyOverview);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const templates = useMemo(() => listStudioTemplateDefinitions(), []);
  const featuredTemplates = templates.filter((template) => template.source === 'recommended');
  const myTemplates = templates.filter((template) => template.source === 'mine');
  const premiumTemplates = templates.filter((template) => template.plan === 'premium');

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
          brand_summary: {
            ...emptyOverview.brand_summary,
            ...data.brand_summary,
          },
        });
        setError(null);
      } catch (err) {
        if (!mounted) return;
        setError(err instanceof Error ? err.message : 'Projetos recentes indisponiveis agora.');
        setOverview(emptyOverview);
      } finally {
        if (mounted) setLoading(false);
      }
    }

    void loadOverview();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <motion.main
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.22 }}
      className="min-h-[calc(100vh-2rem)] text-white"
    >
      <div className="grid gap-5 xl:grid-cols-[228px_minmax(0,1fr)]">
        <aside className="rounded-2xl border border-white/10 bg-white/[0.055] p-4">
          <p className="text-xs font-bold uppercase tracking-[0.22em] text-cyan-300">Studio</p>
          <nav className="mt-4 grid gap-2" aria-label="Studio">
            {studioNav.map((item) => {
              const Icon = item.icon;
              return (
                <Link key={item.label} to={item.path} className="flex items-center gap-3 rounded-xl border border-white/10 bg-black/20 px-3 py-3 text-sm font-bold text-slate-200 hover:border-cyan-300/35 hover:text-white">
                  <Icon size={17} className="text-cyan-200" />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </aside>

        <section className="space-y-8 rounded-2xl border border-white/10 bg-[radial-gradient(circle_at_12%_0%,rgba(192,38,211,0.18),transparent_32%),radial-gradient(circle_at_86%_0%,rgba(34,211,238,0.14),transparent_30%),linear-gradient(180deg,#050507,#0a0a12)] p-5 shadow-[var(--studio-shadow)] md:p-7">
          <div className="mx-auto max-w-4xl text-center">
            <h1 className="font-display text-4xl font-black tracking-tight md:text-5xl">O que vamos criar hoje?</h1>
            <p className="mt-3 text-sm leading-6 text-slate-300">
              Inspire-se, escolha um template e abra o editor com contexto pronto. Nada de canvas vazio como ponto de partida.
            </p>

            <div className="mx-auto mt-6 max-w-3xl rounded-2xl border border-white/10 bg-black/30 p-2 backdrop-blur-xl">
              <div className="flex flex-col gap-2 rounded-xl border border-white/10 bg-white/[0.04] p-2 sm:flex-row sm:items-center">
                <Search className="ml-2 hidden h-5 w-5 text-cyan-200 sm:block" />
                <input
                  aria-label="Buscar no Studio"
                  className="min-w-0 flex-1 rounded-xl bg-transparent px-2 py-3 text-sm text-white outline-none placeholder:text-slate-500"
                  placeholder="Buscar templates, posts, videos, campanhas, hotelaria..."
                />
                <Link to="/app/studio/ai-creative" className="inline-flex items-center justify-center gap-2 rounded-xl bg-[var(--studio-gradient)] px-4 py-3 text-sm font-bold text-white">
                  <Wand2 size={16} /> Magic Studio
                </Link>
              </div>
            </div>
          </div>

          <section>
            <div className="mb-3 flex items-center justify-between">
              <h2 className="font-display text-2xl font-bold">Criar novo</h2>
              <Link to="/app/studio/templates" className="text-xs font-bold text-slate-300 hover:text-white">Explorar templates</Link>
            </div>
            <div className="grid gap-3 md:grid-cols-3 xl:grid-cols-6">
              {createCards.map((card) => {
                const Icon = card.icon;
                return (
                  <Link key={card.label} to={card.path} className="rounded-2xl border border-white/10 bg-white/[0.055] p-4 hover:border-cyan-300/35 hover:bg-white/[0.08]">
                    <Icon className="h-6 w-6 text-cyan-200" />
                    <p className="mt-3 font-bold">{card.label}</p>
                    <p className="mt-1 text-xs leading-5 text-slate-400">{card.description}</p>
                  </Link>
                );
              })}
            </div>
          </section>

          {loading ? (
            <div className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.055] px-4 py-3 text-sm text-slate-300">
              <Loader2 className="h-4 w-4 animate-spin text-cyan-300" /> Carregando dados do Studio...
            </div>
          ) : null}

          {error ? (
            <div className="flex items-center gap-2 rounded-xl border border-amber-300/30 bg-amber-300/10 px-4 py-3 text-sm font-semibold text-amber-100">
              <AlertTriangle className="h-4 w-4" /> {error} As ferramentas continuam funcionando.
            </div>
          ) : null}

          <section className="grid gap-4 xl:grid-cols-[1.4fr_0.6fr]">
            <article className="rounded-2xl border border-fuchsia-300/20 bg-fuchsia-300/10 p-5">
              <p className="text-xs font-bold uppercase tracking-[0.24em] text-fuchsia-100">IA do Dia</p>
              <h2 className="mt-2 font-display text-2xl font-bold">Gerar campanha a partir de uma oferta</h2>
              <p className="mt-2 text-sm leading-6 text-fuchsia-50/80">
                Use um briefing simples para criar story, banner e copy de campanha. O fluxo abre em IA criativa e depende dos providers reais configurados.
              </p>
              <Link to="/app/studio/ai-creative" className="mt-4 inline-flex items-center gap-2 rounded-xl border border-fuchsia-200/35 bg-black/20 px-4 py-3 text-sm font-bold text-white">
                <Sparkles size={16} /> Abrir IA criativa
              </Link>
            </article>
            <article className="rounded-2xl border border-amber-300/25 bg-amber-300/10 p-5">
              <p className="text-xs font-bold uppercase tracking-[0.24em] text-amber-100">Magic Studio</p>
              <h2 className="mt-2 font-display text-2xl font-bold">IA sem sucesso falso</h2>
              <p className="mt-2 text-sm leading-6 text-amber-50/80">
                Remover fundo, expandir imagem e gerar video ficam indisponiveis quando nao houver provider ou endpoint real.
              </p>
            </article>
          </section>

          <TemplateStrip title="Templates em destaque" templates={featuredTemplates.length ? featuredTemplates : templates} />
          <TemplateStrip title="Meus Templates" templates={myTemplates.length ? myTemplates : templates.filter((template) => template.plan === 'free')} />
          <TemplateStrip title="Templates Premium" templates={premiumTemplates} />

          <section>
            <div className="mb-3 flex items-center justify-between">
              <h2 className="font-display text-2xl font-bold">Projetos recentes</h2>
              <Link to="/app/studio/projects" className="text-xs font-bold text-slate-300 hover:text-white">Ver projetos</Link>
            </div>
            {overview.recent_projects.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-white/15 bg-white/[0.05] p-5 text-sm text-slate-300">
                Nenhum projeto recente ainda. Escolha um template para iniciar com estrutura pronta.
              </div>
            ) : (
              <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                {overview.recent_projects.slice(0, 4).map((project) => (
                  <Link key={project.id} to={resolveStudioProjectRoute(project.project_type, project.id)} className="rounded-2xl border border-white/10 bg-white/[0.055] p-4 hover:border-cyan-300/35">
                    <p className="font-bold">{project.title}</p>
                    <p className="mt-1 text-xs text-slate-400">{project.project_type}</p>
                  </Link>
                ))}
              </div>
            )}
          </section>

          <section>
            <div className="mb-3 flex items-center justify-between">
              <h2 className="font-display text-2xl font-bold">Uploads recentes</h2>
              <Link to="/app/studio/assets" className="text-xs font-bold text-slate-300 hover:text-white">Ver uploads</Link>
            </div>
            {overview.recent_exports.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-white/15 bg-white/[0.05] p-5 text-sm text-slate-300">
                Uploads e exportacoes recentes aparecem aqui quando houver historico real.
              </div>
            ) : (
              <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                {overview.recent_exports.slice(0, 4).map((item) => (
                  <a key={item.id} href={item.file_url} className="rounded-2xl border border-white/10 bg-white/[0.055] p-4 hover:border-cyan-300/35">
                    <Upload className="h-5 w-5 text-cyan-200" />
                    <p className="mt-2 font-bold">{item.file_name}</p>
                    <p className="mt-1 text-xs text-slate-400">{item.export_type} - {item.source}</p>
                  </a>
                ))}
              </div>
            )}
          </section>
        </section>
      </div>
    </motion.main>
  );
}
