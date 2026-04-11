import { useRef, useState } from 'react';

import { useStudioV2 } from '../../../hooks/useStudioV2';
import { useToast } from '../../../hooks/useToast';
import { deleteStudioAsset, uploadStudioAsset } from '../../../services/studio.service';

export function AssetsStudioPage() {
  const studio = useStudioV2({ defaultType: 'assets', defaultTitle: 'Assets Studio' });
  const toast = useToast();
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [uploading, setUploading] = useState(false);
  const [deletingAssetId, setDeletingAssetId] = useState<number | null>(null);

  async function handleUploadSelectedFile(file: File | null) {
    if (!file) {
      toast.warning('Selecione um arquivo para upload.');
      return;
    }

    setUploading(true);
    try {
      await uploadStudioAsset({
        file,
        assetType: file.type.startsWith('video/') ? 'video' : 'image',
        projectId: studio.currentProject?.id ?? null,
      });
      await studio.reload();
      toast.success('Upload concluido com sucesso.');
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Falha ao enviar arquivo.');
    } finally {
      setUploading(false);
      if (inputRef.current) inputRef.current.value = '';
    }
  }

  async function handleDelete(assetId: number) {
    setDeletingAssetId(assetId);
    try {
      await deleteStudioAsset(assetId);
      await studio.reload();
      toast.info('Asset removido da biblioteca.');
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Falha ao remover asset.');
    } finally {
      setDeletingAssetId(null);
    }
  }

  return (
    <div className="space-y-4">
      <header className="rounded-3xl border border-white/10 bg-white/5 p-5">
        <p className="text-xs uppercase tracking-[0.24em] text-cyan-300">Assets</p>
        <h1 className="mt-2 font-display text-3xl text-white">Biblioteca visual de logos, produtos e midias</h1>
        <p className="mt-2 text-sm text-slate-300">Upload, organizacao e remocao com retorno visual imediato.</p>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <input
            ref={inputRef}
            type="file"
            accept="image/*,video/*"
            disabled={uploading}
            onChange={(event) => void handleUploadSelectedFile(event.target.files?.[0] ?? null)}
            className="block w-full max-w-sm rounded-xl border border-white/20 bg-black/20 px-3 py-2 text-sm text-slate-200 file:mr-3 file:rounded-lg file:border-0 file:bg-cyan file:px-3 file:py-1 file:text-xs file:font-semibold file:text-ink"
          />
          <span className="text-xs text-slate-400">{uploading ? 'Processando upload...' : 'Formatos: imagem e video'}</span>
        </div>
      </header>

      {studio.assets.length === 0 ? (
        <section className="rounded-2xl border border-dashed border-white/20 bg-black/20 p-6 text-sm text-slate-300">
          <p className="font-semibold text-white">Biblioteca vazia</p>
          <p className="mt-2">1. Envie um arquivo pelo seletor acima.</p>
          <p>2. Acesse qualquer workspace para reutilizar os assets.</p>
          <p>3. Use nomenclatura consistente para facilitar busca por campanha.</p>
        </section>
      ) : null}

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {studio.assets.map((asset) => (
          <article key={asset.id} className="rounded-2xl border border-white/10 bg-black/20 p-4">
            <p className="font-semibold text-white">{asset.name}</p>
            <p className="text-xs text-slate-400">{asset.asset_type}</p>
            <p className="mt-2 text-xs text-slate-500 break-all">{asset.file_url}</p>
            <div className="mt-3 flex justify-end">
              <button
                type="button"
                onClick={() => void handleDelete(asset.id)}
                disabled={deletingAssetId === asset.id}
                className="rounded-lg border border-rose-300/35 px-3 py-1 text-xs text-rose-100 disabled:opacity-60"
              >
                {deletingAssetId === asset.id ? 'Removendo...' : 'Remover'}
              </button>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
