import { Save, Share2, Undo2, Redo2 } from 'lucide-react';

import { StudioSaveIndicator } from './StudioSaveIndicator';

interface StudioTopbarProps {
  projectName: string;
  saveState: 'saved' | 'saving' | 'dirty';
  onSave: () => void;
  onExport: () => void;
}

export function StudioTopbar({ projectName, saveState, onSave, onExport }: StudioTopbarProps) {
  return (
    <header className="sticky top-0 z-20 flex items-center justify-between rounded-3xl border border-cyan-400/20 bg-[linear-gradient(100deg,rgba(3,8,26,0.95),rgba(8,20,44,0.9))] px-4 py-3 shadow-[0_8px_30px_rgba(0,214,255,0.08)] backdrop-blur-xl">
      <div>
        <p className="text-[11px] uppercase tracking-[0.24em] text-cyan-300">AXI Studio</p>
        <p className="font-display text-lg text-white">{projectName}</p>
      </div>
      <div className="flex items-center gap-2">
        <button type="button" className="rounded-xl border border-white/15 px-3 py-2 text-slate-200 hover:border-cyan-300/40 hover:text-white"><Undo2 size={16} /></button>
        <button type="button" className="rounded-xl border border-white/15 px-3 py-2 text-slate-200 hover:border-cyan-300/40 hover:text-white"><Redo2 size={16} /></button>
        <StudioSaveIndicator state={saveState} />
        <button type="button" onClick={onSave} className="inline-flex items-center gap-2 rounded-xl border border-cyan-300/40 bg-cyan-400/10 px-3 py-2 text-sm font-semibold text-cyan-100 hover:bg-cyan-400/20">
          <Save size={15} /> Salvar
        </button>
        <button type="button" onClick={onExport} className="inline-flex items-center gap-2 rounded-xl bg-cyan px-3 py-2 text-sm font-semibold text-ink hover:bg-white">
          <Share2 size={15} /> Exportar
        </button>
      </div>
    </header>
  );
}
