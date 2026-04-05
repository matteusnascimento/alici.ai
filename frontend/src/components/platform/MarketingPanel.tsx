import { useState } from 'react';

import { AdsWorkspace } from '../studio/AdsWorkspace';
import { MarketingWorkspace } from '../studio/MarketingWorkspace';
import { PhotoEditorWorkspace } from '../studio/PhotoEditorWorkspace';
import { PosterWorkspace } from '../studio/PosterWorkspace';
import { ProductPhotoWorkspace } from '../studio/ProductPhotoWorkspace';
import { ProjectsWorkspace } from '../studio/ProjectsWorkspace';
import { StudioHeader } from '../studio/StudioHeader';
import { StudioToolGrid } from '../studio/StudioToolGrid';
import { ToolEmptyState } from '../studio/ToolEmptyState';
import type { StudioToolId } from '../studio/studioTypes';

function renderWorkspace(tool: StudioToolId | null, onNotify: (msg: string) => void) {
  switch (tool) {
    case 'ads':
      return <AdsWorkspace onNotify={onNotify} />;
    case 'product-photos':
      return <ProductPhotoWorkspace onNotify={onNotify} />;
    case 'poster-ai':
      return <PosterWorkspace onNotify={onNotify} />;
    case 'photo-editor':
      return <PhotoEditorWorkspace onNotify={onNotify} />;
    case 'marketing-tools':
      return <MarketingWorkspace onNotify={onNotify} />;
    case 'projects':
      return <ProjectsWorkspace onNotify={onNotify} />;
    default:
      if (!tool) return null;
      return (
        <ToolEmptyState
          title="Workspace em configuracao"
          message="Este modulo ja esta preparado visualmente e com mocks. A proxima etapa e plugar os endpoints de IA no service layer do studio."
        />
      );
  }
}

export function MarketingPanel() {
  const [activeTool, setActiveTool] = useState<StudioToolId | null>(null);
  const [toast, setToast] = useState<string | null>(null);

  function notify(message: string) {
    setToast(message);
    window.setTimeout(() => setToast(null), 2600);
  }

  return (
    <div className="space-y-6">
      <StudioHeader
        onQuickCreate={() => {
          setActiveTool('ads');
          notify('Workspace de Anuncios Inteligentes aberto.');
        }}
        onQuickGenerate={() => notify('Geracao IA acionada em modo mock para demos.')}
      />

      <StudioToolGrid activeTool={activeTool} onSelect={(tool) => setActiveTool(tool)} />

      {activeTool ? (
        <section className="rounded-3xl border border-white/10 bg-white/[0.02] p-4 md:p-5">{renderWorkspace(activeTool, notify)}</section>
      ) : (
        <ToolEmptyState
          title="Selecione uma ferramenta"
          message="Escolha um card acima para abrir um workspace de criacao visual, marketing operacional ou projetos."
        />
      )}

      {toast ? (
        <div className="fixed bottom-6 right-6 z-50 rounded-2xl border border-cyan/30 bg-ink/90 px-4 py-3 text-sm text-cyan shadow-soft backdrop-blur">
          {toast}
        </div>
      ) : null}
    </div>
  );
}
