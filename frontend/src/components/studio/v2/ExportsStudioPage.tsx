import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import { useToast } from '../../../hooks/useToast';
import { listStudioRecentExports } from '../../../services/studio.service';
import type { StudioRecentExportItem } from '../../../types/studioV2';

const routeBySource: Record<string, string> = {
  poster: '/app/studio/tools/ad',
  story: '/app/studio/tools/story',
  ad: '/app/studio/tools/ad',
  'ad-builder': '/app/studio/tools/ad',
  banner: '/app/studio/tools/ad',
  video: '/app/studio/editor/video',
  'video-editor': '/app/studio/editor/video',
  'photo-edit': '/app/studio/tools/photo-editor',
  'photo-editor': '/app/studio/tools/photo-editor',
  'background-remove': '/app/studio/tools/remove-background',
  campaign: '/app/studio/tools/campaign',
  cta: '/app/studio/tools/cta',
};

export function ExportsStudioPage() {
  const toast = useToast();
  const [items, setItems] = useState<StudioRecentExportItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function load() {
      setLoading(true);
      try {
        const data = await listStudioRecentExports(20);
        if (mounted) {
          setItems(data);
          setError(null);
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Falha ao carregar exportacoes.');
          toast.error('Falha de API ao carregar exportacoes.');
        }
      } finally {
        if (mounted) setLoading(false);
      }
    }
    void load();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="space-y-4">
      <header className="rounded-3xl border border-white/10 bg-white/5 p-5">
        <p className="text-xs uppercase tracking-[0.24em] text-cyan-300">Exports</p>
        <h1 className="mt-2 font-display text-3xl text-white">Exportacoes recentes do AXI Studio</h1>
      </header>

      {loading ? <p className="text-sm text-slate-400">Carregando exportacoes...</p> : null}
      {error ? <p className="text-sm text-coral">{error}</p> : null}

      <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {items.map((item) => (
          <article key={item.id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="font-semibold text-white">{item.file_name}</p>
            <p className="text-xs text-slate-400">{item.export_type.toUpperCase()} • {new Date(item.created_at).toLocaleString('pt-BR')}</p>
            <p className="mt-1 text-xs text-slate-500">Origem: {item.source}</p>
            <div className="mt-3 flex gap-2">
              <a href={item.file_url} onClick={() => toast.success('Download iniciado.')} className="rounded-lg border border-cyan-300/45 px-3 py-1 text-xs text-cyan-100">Baixar</a>
              <Link to={routeBySource[item.source] || '/app/studio/projects'} onClick={() => toast.info('Abrindo projeto da exportacao.')} className="rounded-lg border border-white/20 px-3 py-1 text-xs text-white">Abrir</Link>
            </div>
          </article>
        ))}
        {!loading && items.length === 0 ? <p className="text-sm text-slate-400">Nenhuma exportacao encontrada.</p> : null}
      </section>
    </div>
  );
}
