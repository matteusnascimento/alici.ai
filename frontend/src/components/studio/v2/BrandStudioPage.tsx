import { useEffect, useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';

import { useStudioV2 } from '../../../hooks/useStudioV2';
import { getStudioBrandSummary } from '../../../services/studio.service';
import type { StudioBrandSummary } from '../../../types/studioV2';

const tabs = ['logos', 'templates', 'palettes', 'assets'] as const;
type Tab = (typeof tabs)[number];

function isTab(value: string | null): value is Tab {
  return !!value && tabs.includes(value as Tab);
}

export function BrandStudioPage() {
  const [searchParams] = useSearchParams();
  const activeTab: Tab = isTab(searchParams.get('tab')) ? (searchParams.get('tab') as Tab) : 'logos';
  const studio = useStudioV2({ defaultType: 'brand', defaultTitle: 'Biblioteca da Marca' });
  const [summary, setSummary] = useState<StudioBrandSummary | null>(null);

  useEffect(() => {
    void getStudioBrandSummary().then(setSummary).catch(() => setSummary(null));
  }, []);

  const filteredAssets = useMemo(() => {
    if (activeTab === 'logos') {
      return studio.assets.filter((asset) => asset.asset_type.includes('logo'));
    }
    if (activeTab === 'palettes') {
      return studio.assets.filter((asset) => asset.asset_type.includes('palette'));
    }
    return studio.assets;
  }, [activeTab, studio.assets]);

  return (
    <div className="space-y-4">
      <header className="rounded-3xl border border-white/10 bg-white/5 p-5">
        <p className="text-xs uppercase tracking-[0.24em] text-cyan-300">Brand</p>
        <h1 className="mt-2 font-display text-3xl text-white">Biblioteca de marca e atalhos operacionais</h1>
        <p className="mt-2 text-sm text-slate-300">Gerencie logos, templates, paletas e assets em um unico lugar.</p>
      </header>

      <section className="grid gap-2 md:grid-cols-4">
        <Link to="/app/studio/brand?tab=logos" className={`rounded-xl border px-3 py-2 text-sm ${activeTab === 'logos' ? 'border-cyan-300/55 bg-cyan-400/10 text-cyan-100' : 'border-white/10 bg-black/20 text-slate-200'}`}>
          Logos ({summary?.logos_count ?? 0})
        </Link>
        <Link to="/app/studio/brand?tab=templates" className={`rounded-xl border px-3 py-2 text-sm ${activeTab === 'templates' ? 'border-cyan-300/55 bg-cyan-400/10 text-cyan-100' : 'border-white/10 bg-black/20 text-slate-200'}`}>
          Templates ({summary?.templates_count ?? 0})
        </Link>
        <Link to="/app/studio/brand?tab=palettes" className={`rounded-xl border px-3 py-2 text-sm ${activeTab === 'palettes' ? 'border-cyan-300/55 bg-cyan-400/10 text-cyan-100' : 'border-white/10 bg-black/20 text-slate-200'}`}>
          Paletas ({summary?.palettes_count ?? 0})
        </Link>
        <Link to="/app/studio/brand?tab=assets" className={`rounded-xl border px-3 py-2 text-sm ${activeTab === 'assets' ? 'border-cyan-300/55 bg-cyan-400/10 text-cyan-100' : 'border-white/10 bg-black/20 text-slate-200'}`}>
          Assets ({summary?.assets_count ?? 0})
        </Link>
      </section>

      {activeTab === 'templates' ? (
        <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {studio.templates.map((template) => (
            <article key={template.id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="font-semibold text-white">{template.name}</p>
              <p className="text-xs text-slate-400">{template.category}</p>
              <p className="mt-2 text-xs text-slate-500">Criado em {new Date(template.created_at).toLocaleString('pt-BR')}</p>
            </article>
          ))}
          {studio.templates.length === 0 ? <p className="text-sm text-slate-400">Nenhum template disponivel.</p> : null}
        </section>
      ) : (
        <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {filteredAssets.map((asset) => (
            <article key={asset.id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
              <p className="font-semibold text-white">{asset.name}</p>
              <p className="text-xs text-slate-400">{asset.asset_type}</p>
              <p className="mt-2 text-xs text-slate-500">{asset.file_url}</p>
            </article>
          ))}
          {filteredAssets.length === 0 ? <p className="text-sm text-slate-400">Nenhum asset nesta categoria.</p> : null}
        </section>
      )}
    </div>
  );
}
