import type { StudioAsset } from '../../../types/studioV2';

interface StudioAssetsPanelProps {
  assets: StudioAsset[];
}

export function StudioAssetsPanel({ assets }: StudioAssetsPanelProps) {
  return (
    <div className="rounded-2xl border border-white/10 bg-black/20 p-3">
      <p className="mb-2 text-xs uppercase tracking-[0.16em] text-slate-400">Assets</p>
      <div className="grid grid-cols-2 gap-2">
        {assets.slice(0, 6).map((asset) => (
          <div key={asset.id} className="rounded-lg border border-white/10 bg-white/5 p-2 text-xs text-slate-300">
            <p className="truncate font-semibold text-white">{asset.name}</p>
            <p className="text-slate-400">{asset.asset_type}</p>
          </div>
        ))}
        {assets.length === 0 ? <p className="col-span-2 text-xs text-slate-400">Sem assets ainda.</p> : null}
      </div>
    </div>
  );
}
