import { Crown, LayoutTemplate, Lock, Search, Sparkles } from 'lucide-react';
import { useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';

import { STUDIO_TEMPLATE_CATEGORIES } from '../../../data/studioTemplates';
import { listStudioTemplateDefinitions } from '../../../services/studioTemplate.service';
import type { StudioTemplateDefinition } from '../../../types/studioTemplate';

function templateEditorRoute(template: StudioTemplateDefinition) {
  const target = template.type === 'video' || template.type === 'story' ? 'video' : 'design';
  return `/app/studio/editor/${target}?mode=new&template=${template.id}`;
}

function TemplateCard({ template }: { template: StudioTemplateDefinition }) {
  const premium = template.plan === 'premium';
  const route = templateEditorRoute(template);
  return (
    <article className="overflow-hidden rounded-3xl border border-white/10 bg-white/[0.055] shadow-[var(--studio-tile-shadow)]">
      <div className="aspect-[4/3] bg-[radial-gradient(circle_at_28%_18%,rgba(34,211,238,0.24),transparent_34%),linear-gradient(135deg,#111827,#312e81_48%,#0e7490)] p-4">
        <div className="flex h-full flex-col justify-between rounded-2xl border border-white/15 bg-black/20 p-4">
          <span className="w-fit rounded-full bg-black/45 px-3 py-1 text-[11px] font-bold uppercase tracking-[0.18em] text-cyan-100">{template.format}</span>
          <LayoutTemplate className="h-10 w-10 text-white/75" />
        </div>
      </div>
      <div className="p-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-[11px] font-bold uppercase tracking-[0.2em] text-cyan-300">{template.category}</p>
            <h2 className="mt-1 font-display text-xl font-bold text-white">{template.name}</h2>
          </div>
          <span className={premium ? 'inline-flex items-center gap-1 rounded-full bg-fuchsia-300/15 px-2 py-1 text-[11px] font-bold text-fuchsia-100' : 'rounded-full bg-emerald-300/15 px-2 py-1 text-[11px] font-bold text-emerald-100'}>
            {premium ? <Crown size={12} /> : null}
            {premium ? 'Premium' : 'Free'}
          </span>
        </div>
        <p className="mt-2 text-xs text-slate-400">{template.type} - {template.format}</p>
        <p className="mt-1 line-clamp-1 text-xs text-slate-500">{template.tags.join(' / ')}</p>
        <div className="mt-4 grid gap-2">
          <Link to={route} className="inline-flex w-full items-center justify-center gap-2 rounded-2xl border border-cyan-300/35 bg-cyan-300/10 px-4 py-3 text-sm font-bold text-cyan-50 hover:bg-cyan-300/18">
            Usar template
          </Link>
          {premium ? (
            <button type="button" className="inline-flex items-center justify-center gap-2 rounded-2xl border border-fuchsia-300/30 bg-fuchsia-300/10 px-4 py-2.5 text-xs font-bold text-fuchsia-100">
              <Lock size={13} /> Bloqueado por plano
            </button>
          ) : null}
        </div>
      </div>
    </article>
  );
}

export function TemplatesStudioPage() {
  const [searchParams] = useSearchParams();
  const initialCategory = searchParams.get('category') || 'Todos';
  const initialSection = searchParams.get('section') || 'all';
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState(initialCategory);
  const [section, setSection] = useState(initialSection);
  const templates = useMemo(() => listStudioTemplateDefinitions(), []);

  const filtered = templates.filter((template) => {
    const matchesCategory = category === 'Todos' || template.category === category;
    const matchesSection =
      section === 'all' ||
      (section === 'mine' && template.source === 'mine') ||
      (section === 'premium' && template.plan === 'premium') ||
      (section === 'recommended' && template.source === 'recommended');
    const haystack = `${template.name} ${template.category} ${template.tags.join(' ')}`.toLowerCase();
    return matchesCategory && matchesSection && haystack.includes(query.toLowerCase());
  });

  return (
    <main className="min-h-[calc(100vh-2rem)] rounded-[2rem] border border-white/10 bg-[radial-gradient(circle_at_14%_0%,rgba(192,38,211,0.18),transparent_34%),linear-gradient(180deg,#050507,#0a0a12)] p-5 text-white shadow-[var(--studio-shadow)] md:p-7">
      <header className="rounded-3xl border border-white/10 bg-white/[0.055] p-5 backdrop-blur-xl">
        <p className="text-xs font-bold uppercase tracking-[0.28em] text-cyan-300">Templates</p>
        <div className="mt-3 flex flex-wrap items-end justify-between gap-4">
          <div>
            <h1 className="font-display text-3xl font-black">Templates para comecar rapido</h1>
            <p className="mt-2 max-w-2xl text-sm text-slate-300">Tudo comeca pelo template: marketing, hotelaria, social, premium e modelos criados pelo usuario.</p>
          </div>
          <Link to="/app/studio/editor/design?mode=new" className="inline-flex items-center gap-2 rounded-2xl bg-[var(--studio-gradient)] px-4 py-2.5 text-sm font-bold text-white">
            <Sparkles size={16} /> Criar novo design
          </Link>
        </div>
        <div className="mt-5 flex flex-col gap-3 lg:flex-row">
          <label className="flex min-w-0 flex-1 items-center gap-2 rounded-2xl border border-white/10 bg-black/25 px-3 py-2">
            <Search size={16} className="text-cyan-200" />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Buscar templates" className="min-w-0 flex-1 bg-transparent py-2 text-sm text-white outline-none" />
          </label>
          <div className="flex gap-2 overflow-x-auto">
            {['all', 'mine', 'premium', 'recommended'].map((item) => (
              <button key={item} type="button" onClick={() => setSection(item)} className={section === item ? 'shrink-0 rounded-2xl border border-cyan-300/40 bg-cyan-300/12 px-4 py-2 text-sm font-bold text-cyan-50' : 'shrink-0 rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-2 text-sm font-bold text-slate-300'}>
                {item === 'all' ? 'Todos' : item === 'mine' ? 'Meus Templates' : item === 'premium' ? 'Templates Premium' : 'Recomendados'}
              </button>
            ))}
          </div>
        </div>
      </header>

      <div className="mt-5 flex gap-2 overflow-x-auto pb-2">
        {['Todos', ...STUDIO_TEMPLATE_CATEGORIES].map((item) => (
          <button key={item} type="button" onClick={() => setCategory(item)} className={category === item ? 'shrink-0 rounded-full border border-cyan-300/40 bg-cyan-300/12 px-4 py-2 text-sm font-bold text-cyan-50' : 'shrink-0 rounded-full border border-white/10 bg-white/[0.055] px-4 py-2 text-sm font-semibold text-slate-200'}>
            {item}
          </button>
        ))}
      </div>

      <section className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {filtered.map((template) => <TemplateCard key={template.id} template={template} />)}
      </section>
    </main>
  );
}
