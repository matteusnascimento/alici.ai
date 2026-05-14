import { useState } from 'react';

import { useStudioV2 } from '../../../hooks/useStudioV2';
import { useToast } from '../../../hooks/useToast';
import { studioCreateAd } from '../../../services/studio.service';
import { StudioCanvas } from './StudioCanvas';
import { StudioInspectorPanel } from './StudioInspectorPanel';
import { StudioShell } from './StudioShell';

export function BannerStudioPage() {
  const studio = useStudioV2({ defaultType: 'ad', defaultTitle: 'Criacao de Anuncio' });
  const { pushToast } = useToast();
  const [product, setProduct] = useState('Consultoria de Marketing');
  const [offer, setOffer] = useState('30% OFF para novos clientes');
  const [audience, setAudience] = useState('Empreendedores locais');
  const [channel, setChannel] = useState('Meta Ads');
  const [prompt, setPrompt] = useState('Anuncio de performance com foco em conversao imediata.');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  async function handleCreateAd() {
    setLoading(true);
    try {
      const result = await studioCreateAd({ product, offer, audience, channel, prompt });
      setStatus(result.message);
      await studio.reload();
      pushToast('Anuncio base criado com IA.', 'success');
    } catch (err) {
      setStatus(err instanceof Error ? err.message : 'Falha ao criar anuncio.');
      pushToast('Falha ao criar anuncio.', 'error');
    } finally {
      setLoading(false);
    }
  }

  return (
    <StudioShell
      projectName={studio.projectName}
      saveState={loading ? 'saving' : studio.saveState}
      onSave={() => void studio.saveProject({ status: 'saved', metadata: { product, offer, audience, channel, prompt } })}
      onExport={() => void studio.exportProject('png')}
      center={(
        <StudioCanvas title="Ad Workspace" subtitle="Briefing completo para produto, oferta, publico e canal com IA gerando copy + base visual">
          <div className="grid h-full place-items-center rounded-2xl border border-dashed border-cyan-300/30 bg-black/30 p-6 text-center">
            <div>
              <p className="font-display text-2xl text-white">{product}</p>
              <p className="mt-2 text-slate-300">{offer}</p>
              <p className="mt-2 text-xs text-slate-400">Publico: {audience} • Canal: {channel}</p>
              <button type="button" onClick={() => void handleCreateAd()} disabled={loading} className="mt-4 rounded-xl bg-cyan px-4 py-2 text-sm font-semibold text-ink disabled:opacity-70">
                {loading ? 'Gerando anuncio...' : 'Gerar anuncio com IA'}
              </button>
              {status ? <p className="mt-3 text-xs text-cyan-100">{status}</p> : null}
            </div>
          </div>
        </StudioCanvas>
      )}
      right={(
        <StudioInspectorPanel title="Briefing de campanha">
          <label className="text-xs text-slate-400">Produto</label>
          <input value={product} onChange={(event) => setProduct(event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white" />
          <label className="text-xs text-slate-400">Oferta</label>
          <input value={offer} onChange={(event) => setOffer(event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white" />
          <label className="text-xs text-slate-400">Publico</label>
          <input value={audience} onChange={(event) => setAudience(event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white" />
          <label className="text-xs text-slate-400">Canal</label>
          <input value={channel} onChange={(event) => setChannel(event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white" />
          <label className="text-xs text-slate-400">Prompt</label>
          <textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} className="min-h-24 w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white" />
        </StudioInspectorPanel>
      )}
    />
  );
}
