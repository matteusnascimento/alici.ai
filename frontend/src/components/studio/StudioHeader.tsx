import { Search, Sparkles, Wand2 } from 'lucide-react';

interface StudioHeaderProps {
  onQuickCreate: () => void;
  onQuickGenerate: () => void;
}

export function StudioHeader({ onQuickCreate, onQuickGenerate }: StudioHeaderProps) {
  return (
    <header className="rounded-3xl border border-white/10 bg-[radial-gradient(circle_at_top_right,_rgba(110,231,249,0.17),transparent_60%)] p-6 md:p-8">
      <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-cyan">Plataforma AXI</p>
          <h1 className="mt-3 font-display text-3xl text-white md:text-4xl">AXI Studio</h1>
          <p className="mt-3 max-w-2xl text-sm text-slate-300 md:text-base">
            Criacao visual, campanhas e midia com IA em um unico workspace.
          </p>
        </div>
        <div className="flex w-full max-w-xl flex-col gap-3 sm:flex-row sm:items-center">
          <div className="flex flex-1 items-center gap-2 rounded-2xl border border-white/15 bg-ink/50 px-3 py-2 text-slate-300">
            <Search size={16} />
            <input
              className="w-full bg-transparent text-sm text-white outline-none"
              placeholder="Buscar ferramenta, projeto ou template"
            />
          </div>
          <button
            type="button"
            onClick={onQuickCreate}
            className="inline-flex items-center justify-center gap-2 rounded-2xl border border-white/15 bg-white/[0.06] px-4 py-2 text-sm text-white transition hover:border-cyan/40"
          >
            <Wand2 size={15} /> Novo
          </button>
          <button
            type="button"
            onClick={onQuickGenerate}
            className="inline-flex items-center justify-center gap-2 rounded-2xl border border-cyan/35 bg-cyan/10 px-4 py-2 text-sm text-cyan transition hover:bg-cyan/20"
          >
            <Sparkles size={15} /> Gerar com IA
          </button>
        </div>
      </div>
    </header>
  );
}
