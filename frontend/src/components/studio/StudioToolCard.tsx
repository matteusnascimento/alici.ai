import type { StudioTool } from './studioTypes';

interface StudioToolCardProps {
  tool: StudioTool;
  active: boolean;
  onClick: () => void;
}

export function StudioToolCard({ tool, active, onClick }: StudioToolCardProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={[
        'group rounded-2xl border p-4 text-left transition duration-200',
        active
          ? 'border-cyan/45 bg-cyan/10 shadow-[inset_0_0_25px_rgba(110,231,249,0.13)]'
          : 'border-white/10 bg-white/[0.03] hover:border-white/20 hover:bg-white/[0.06]',
      ].join(' ')}
    >
      <div className="inline-flex h-11 w-11 items-center justify-center rounded-xl bg-ink/70 text-cyan">
        <tool.icon size={18} />
      </div>
      <h3 className="mt-4 font-semibold text-white">{tool.title}</h3>
      <p className="mt-2 text-sm text-slate-300">{tool.description}</p>
    </button>
  );
}
