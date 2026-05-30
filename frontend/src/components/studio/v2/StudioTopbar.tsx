import { ArrowLeft, Save, Share2, Undo2, Redo2, Copy } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { StudioSaveIndicator } from './StudioSaveIndicator';

interface StudioTopbarProps {
  projectName: string;
  designType?: string;
  saveState: 'saved' | 'saving' | 'dirty';
  onSave: () => void;
  onExport: () => void;
  onDuplicate?: () => void;
  onBackHome?: () => void;
}

export function StudioTopbar({ projectName, designType = 'Editor', saveState, onSave, onExport, onDuplicate, onBackHome }: StudioTopbarProps) {
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-20 flex min-h-[68px] items-center justify-between gap-3 border-b border-white/10 bg-[linear-gradient(100deg,rgba(8,8,12,0.96),rgba(17,12,28,0.92))] px-4 py-3 shadow-[0_14px_42px_rgba(0,0,0,0.28)] backdrop-blur-xl">
      <div className="flex min-w-0 items-center gap-3">
        <button type="button" className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-white/15 text-slate-200 transition hover:border-cyan-300/40 hover:text-white" onClick={() => (onBackHome ? onBackHome() : navigate('/app/studio'))} title="Voltar para a home do Studio" aria-label="Voltar">
          <ArrowLeft size={17} />
        </button>
        <div className="min-w-0">
          <p className="truncate font-display text-lg text-white">{projectName}</p>
          <p className="text-xs font-semibold text-slate-400">{designType}</p>
        </div>
      </div>
      <div className="flex shrink-0 items-center gap-2">
        <button type="button" className="rounded-xl border border-white/15 px-3 py-2 text-slate-200 hover:border-cyan-300/40 hover:text-white" title="Desfazer"><Undo2 size={16} /></button>
        <button type="button" className="rounded-xl border border-white/15 px-3 py-2 text-slate-200 hover:border-cyan-300/40 hover:text-white" title="Refazer"><Redo2 size={16} /></button>
        {onDuplicate ? (
          <button type="button" className="rounded-xl border border-white/15 px-3 py-2 text-slate-200 hover:border-cyan-300/40 hover:text-white" title="Duplicar projeto" onClick={() => onDuplicate()}>
            <Copy size={16} />
          </button>
        ) : null}
        <StudioSaveIndicator state={saveState} />
        <button type="button" onClick={onSave} className="inline-flex items-center gap-2 rounded-xl border border-cyan-300/40 bg-cyan-400/10 px-3 py-2 text-sm font-semibold text-cyan-100 hover:bg-cyan-400/20">
          <Save size={15} /> Salvar
        </button>
        <button type="button" onClick={onExport} className="inline-flex items-center gap-2 rounded-xl bg-[var(--studio-gradient)] px-3 py-2 text-sm font-semibold text-white shadow-[0_0_24px_rgba(192,38,211,0.22)] hover:brightness-110">
          <Share2 size={15} /> Exportar
        </button>
      </div>
    </header>
  );
}
