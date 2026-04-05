import type { ReactNode } from 'react';
import { Bot, Plus, Save } from 'lucide-react';

interface MarketingHeaderProps {
  onNewCampaign: () => void;
  onGenerateWithAi: () => void;
  onSaveTemplate: () => void;
}

function HeaderButton({ label, onClick, icon }: { label: string; onClick: () => void; icon: ReactNode }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="inline-flex items-center justify-center gap-2 rounded-2xl border border-white/15 bg-white/[0.06] px-4 py-2 text-sm text-slate-100 transition hover:border-cyan/40 hover:text-cyan"
    >
      {icon}
      {label}
    </button>
  );
}

export function MarketingHeader({ onNewCampaign, onGenerateWithAi, onSaveTemplate }: MarketingHeaderProps) {
  return (
    <header className="rounded-3xl border border-white/10 bg-[radial-gradient(circle_at_top,_rgba(110,231,249,0.12),transparent_65%)] p-6 md:p-8">
      <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-cyan">Plataforma AXI</p>
          <h1 className="mt-3 font-display text-3xl text-white md:text-4xl">AXI Growth Studio</h1>
          <p className="mt-3 max-w-2xl text-sm text-slate-300 md:text-base">
            Campanhas, criativos, conteudo e funis em um unico workspace.
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <HeaderButton label="Nova campanha" onClick={onNewCampaign} icon={<Plus size={16} />} />
          <HeaderButton label="Gerar com IA" onClick={onGenerateWithAi} icon={<Bot size={16} />} />
          <HeaderButton label="Salvar template" onClick={onSaveTemplate} icon={<Save size={16} />} />
        </div>
      </div>
    </header>
  );
}
