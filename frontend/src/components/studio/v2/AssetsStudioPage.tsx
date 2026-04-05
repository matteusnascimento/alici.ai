import { useStudioV2 } from '../../../hooks/useStudioV2';

export function AssetsStudioPage() {
  const studio = useStudioV2({ defaultType: 'assets', defaultTitle: 'Assets Studio' });

  return (
    <div className="space-y-4">
      <header className="rounded-3xl border border-white/10 bg-white/5 p-5">
        <p className="text-xs uppercase tracking-[0.24em] text-cyan-300">Assets</p>
        <h1 className="mt-2 font-display text-3xl text-white">Biblioteca visual de logos, produtos e midias</h1>
      </header>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {studio.assets.map((asset) => (
          <article key={asset.id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="font-semibold text-white">{asset.name}</p>
            <p className="text-xs text-slate-400">{asset.asset_type}</p>
            <p className="mt-2 text-xs text-slate-500">{asset.file_url}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
