import { useMemo, useState } from 'react';

import { useStudioV2 } from '../../../hooks/useStudioV2';
import { studioGeneratePoster, studioGenerateVariations } from '../../../services/studio.service';
import { StudioAssetsPanel } from './StudioAssetsPanel';
import { StudioBottomDock } from './StudioBottomDock';
import { StudioCanvas } from './StudioCanvas';
import { StudioExportModal } from './StudioExportModal';
import { StudioHistoryPanel } from './StudioHistoryPanel';
import { StudioInspectorPanel } from './StudioInspectorPanel';
import { StudioLayersPanel } from './StudioLayersPanel';
import { StudioPromptBar } from './StudioPromptBar';
import { StudioShell } from './StudioShell';
import { StudioTemplatesPanel } from './StudioTemplatesPanel';
import { StudioToolRail } from './StudioToolRail';
import { StudioVariationStrip } from './StudioVariationStrip';

const posterTools = ['Templates', 'Assets', 'Uploads', 'Elementos', 'Texto', 'Brand'];

export function PosterStudioPage() {
  const studio = useStudioV2({ defaultType: 'poster', defaultTitle: 'Poster com IA' });
  const [objective, setObjective] = useState('Conversao');
  const [audience, setAudience] = useState('Ecommerce local');
  const [tone, setTone] = useState('Premium moderno');
  const [offer, setOffer] = useState('Frete gratis hoje');
  const [cta, setCta] = useState('Comprar agora');
  const [prompt, setPrompt] = useState('Crie um poster de oferta premium para final de semana com foco em conversao');
  const [activeTool, setActiveTool] = useState(posterTools[0]);
  const [openExport, setOpenExport] = useState(false);
  const [variationId, setVariationId] = useState<string | null>('A');
  const [variationList, setVariationList] = useState<Array<{ id: string; title: string; subtitle: string }>>([
    { id: 'A', title: 'Versao A', subtitle: 'Foco em urgencia' },
    { id: 'B', title: 'Versao B', subtitle: 'Foco em prova social' },
    { id: 'C', title: 'Versao C', subtitle: 'Foco em valor' },
  ]);

  const canvasText = useMemo(() => {
    const selected = variationList.find((item) => item.id === variationId);
    return selected ? `${selected.title} - ${selected.subtitle}` : 'Selecione uma variacao';
  }, [variationId, variationList]);

  async function handleGenerate() {
    if (!studio.currentProject) return;
    const result = await studioGeneratePoster({
      project_id: studio.currentProject.id,
      prompt,
      objective,
      audience,
      tone,
      offer,
      cta,
      style: 'premium-neon',
      options: { ratio: '1:1' },
    });

    const rawVariations = Array.isArray(result.result.variations) ? result.result.variations : [];
    const mapped = rawVariations
      .filter((item): item is Record<string, unknown> => typeof item === 'object' && item !== null)
      .map((item, index) => ({
        id: String(item.id || index + 1),
        title: String(item.id || `V${index + 1}`),
        subtitle: String(item.headline || 'Nova variacao'),
      }));

    if (mapped.length > 0) {
      setVariationList(mapped);
      setVariationId(mapped[0].id);
    }
    studio.setSaveState('dirty');
  }

  async function handleGenerateVariation() {
    if (!studio.currentProject) return;
    const result = await studioGenerateVariations({
      project_id: studio.currentProject.id,
      prompt,
      options: { objective, audience, tone, offer, cta },
    });

    const rawVariations = Array.isArray(result.result.variations) ? result.result.variations : [];
    const mapped = rawVariations
      .filter((item): item is Record<string, unknown> => typeof item === 'object' && item !== null)
      .map((item, index) => ({
        id: String(item.id || index + 1),
        title: `Versao ${String(item.id || index + 1)}`,
        subtitle: String(item.headline || 'Nova variacao'),
      }));

    if (mapped.length > 0) {
      setVariationList(mapped);
      setVariationId(mapped[0].id);
    }
    studio.setSaveState('dirty');
  }

  return (
    <>
      <StudioShell
        projectName={studio.projectName}
        saveState={studio.saveState}
        onSave={() => void studio.saveProject({ status: 'saved', metadata: { objective, audience, tone, offer, cta } })}
        onExport={() => setOpenExport(true)}
        leftRail={<StudioToolRail tools={posterTools} activeTool={activeTool} onSelect={setActiveTool} />}
        center={(
          <div className="space-y-4">
            <StudioPromptBar value={prompt} onChange={setPrompt} onGenerate={() => void handleGenerate()} placeholder="Descreva o criativo que voce quer gerar" />
            <StudioCanvas title="Poster Canvas" subtitle="Preview ao vivo, zoom, margens de seguranca e edicao direta no canvas">
              <div className="grid h-full place-items-center rounded-2xl border border-dashed border-cyan-300/30 bg-black/30 p-6 text-center">
                <div>
                  <p className="font-display text-4xl text-white">{offer}</p>
                  <p className="mt-2 text-slate-300">{canvasText}</p>
                  <button type="button" className="mt-4 rounded-xl bg-cyan px-4 py-2 text-sm font-semibold text-ink">{cta}</button>
                </div>
              </div>
            </StudioCanvas>
          </div>
        )}
        right={(
          <StudioInspectorPanel title="AI Poster Assistant">
            <label className="text-xs text-slate-400">Objetivo</label>
            <input value={objective} onChange={(event) => setObjective(event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white" />
            <label className="text-xs text-slate-400">Publico</label>
            <input value={audience} onChange={(event) => setAudience(event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white" />
            <label className="text-xs text-slate-400">Tom</label>
            <input value={tone} onChange={(event) => setTone(event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white" />
            <label className="text-xs text-slate-400">Oferta</label>
            <input value={offer} onChange={(event) => setOffer(event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white" />
            <label className="text-xs text-slate-400">CTA</label>
            <input value={cta} onChange={(event) => setCta(event.target.value)} className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white" />
            <button type="button" onClick={() => void handleGenerateVariation()} className="w-full rounded-xl border border-cyan-300/40 px-3 py-2 text-sm text-cyan-100">
              Generate new variation
            </button>
            <button type="button" onClick={() => void studio.saveVersion(`Poster ${new Date().toLocaleTimeString('pt-BR')}`, { canvas_data: { offer, cta }, timeline_data: { variationId } })} className="w-full rounded-xl border border-white/20 px-3 py-2 text-sm text-white">
              Improve copy
            </button>
            <button type="button" className="w-full rounded-xl border border-white/20 px-3 py-2 text-sm text-white">Try premium style</button>
            <button type="button" className="w-full rounded-xl border border-white/20 px-3 py-2 text-sm text-white">Create story version</button>
            <button type="button" className="w-full rounded-xl border border-white/20 px-3 py-2 text-sm text-white">Create ad version</button>
            <StudioLayersPanel layers={[{ id: 'l1', name: 'Background' }, { id: 'l2', name: 'Headline' }, { id: 'l3', name: 'CTA' }]} />
            <StudioAssetsPanel assets={studio.assets} />
            <StudioTemplatesPanel templates={studio.templates} onApply={(templateId) => void studio.applyTemplate(templateId)} />
            <StudioHistoryPanel versions={studio.versions} />
          </StudioInspectorPanel>
        )}
        bottom={(
          <StudioBottomDock>
            <StudioVariationStrip variations={variationList} selected={variationId} onSelect={setVariationId} />
          </StudioBottomDock>
        )}
      />
      <StudioExportModal
        open={openExport}
        onClose={() => setOpenExport(false)}
        onExport={(format) => {
          setOpenExport(false);
          void studio.exportProject(format);
        }}
      />
    </>
  );
}
