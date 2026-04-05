interface StudioToolRailProps {
  tools: string[];
  activeTool: string;
  onSelect: (tool: string) => void;
}

export function StudioToolRail({ tools, activeTool, onSelect }: StudioToolRailProps) {
  return (
    <div className="flex gap-2 overflow-x-auto rounded-2xl border border-white/10 bg-black/25 p-2 md:flex-col md:overflow-visible md:p-1">
      {tools.map((tool) => (
        <button
          key={tool}
          type="button"
          onClick={() => onSelect(tool)}
          className={`whitespace-nowrap rounded-xl px-3 py-2 text-xs font-semibold uppercase tracking-[0.09em] transition ${activeTool === tool ? 'bg-cyan text-ink' : 'bg-white/5 text-slate-300 hover:bg-white/10 hover:text-white'}`}
        >
          {tool}
        </button>
      ))}
    </div>
  );
}
