import { useState } from 'react';

import { useStudioV2 } from '../../../hooks/useStudioV2';
import { useToast } from '../../../hooks/useToast';
import { studioBackgroundRemove } from '../../../services/studio.service';
import { StudioCanvas } from './StudioCanvas';
import { StudioInspectorPanel } from './StudioInspectorPanel';
import { StudioShell } from './StudioShell';

export function RemoveBackgroundStudioPage() {
  const studio = useStudioV2({ defaultType: 'background-remove', defaultTitle: 'Remover Fundo' });
  const { pushToast } = useToast();
  const [assetUrl, setAssetUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [outputUrl, setOutputUrl] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);

  async function handleProcess() {
    if (!assetUrl.trim()) {
      setStatus('Informe uma URL publica de imagem ou use o upload no editor antes de processar.');
      pushToast('Informe uma imagem real para remover o fundo.', 'error');
      return;
    }
    setLoading(true);
    try {
      const response = await studioBackgroundRemove({
        project_id: studio.currentProject?.id,
        asset_url: assetUrl,
        options: { softness: 0.45 },
      });
      setOutputUrl((response.generation?.result.output_url as string) || null);
      setStatus(response.message);
      studio.setSaveState('dirty');
      pushToast('Fundo removido com sucesso.', 'success');
      if (!response.generation?.result.output_url) {
        pushToast('Processado sem URL final. Verifique as opcoes de saida.', 'warning');
      }
    } catch (err) {
      setStatus(err instanceof Error ? err.message : 'Falha no processamento de fundo.');
      pushToast('Falha ao remover fundo.', 'error');
    } finally {
      setLoading(false);
    }
  }

  return (
    <StudioShell
      projectName={studio.projectName}
      saveState={loading ? 'saving' : studio.saveState}
      onSave={() => void studio.saveProject({ status: 'saved', metadata: { assetUrl, outputUrl } })}
      onExport={() => void studio.exportProject('png')}
      center={(
        <StudioCanvas title="Remocao de Fundo" subtitle="Upload/URL, processamento backend e preview before/after com salvamento no projeto">
          <div className="grid h-full gap-3 rounded-2xl border border-white/10 bg-black/25 p-4 md:grid-cols-2">
            <div className="rounded-xl border border-white/10 bg-black/25 p-3">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Antes</p>
              <p className="mt-2 break-all text-xs text-slate-400">{assetUrl || 'Nenhuma imagem selecionada.'}</p>
            </div>
            <div className="rounded-xl border border-white/10 bg-black/25 p-3">
              <p className="text-xs uppercase tracking-[0.2em] text-cyan-200">Depois</p>
              <p className="mt-2 text-xs text-slate-300">{outputUrl || 'Nenhum processamento ainda.'}</p>
            </div>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <button type="button" onClick={() => void handleProcess()} disabled={loading} className="rounded-xl bg-cyan px-4 py-2 text-sm font-semibold text-ink disabled:opacity-70">
              {loading ? 'Processando...' : 'Remover fundo'}
            </button>
            {outputUrl ? <a href={outputUrl} className="rounded-xl border border-cyan-300/45 px-4 py-2 text-sm text-cyan-100">Download</a> : null}
          </div>
          {status ? <p className="mt-2 text-xs text-cyan-100">{status}</p> : null}
        </StudioCanvas>
      )}
      right={(
        <StudioInspectorPanel title="Parametros de recorte">
          <label className="text-xs text-slate-400">URL da imagem</label>
          <input value={assetUrl} onChange={(event) => setAssetUrl(event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white" placeholder="https://..." />
          <p className="text-xs text-slate-400">Use uma URL publica real ou envie a imagem pelo editor unificado. Nao usamos imagens de exemplo falsas.</p>
        </StudioInspectorPanel>
      )}
    />
  );
}
