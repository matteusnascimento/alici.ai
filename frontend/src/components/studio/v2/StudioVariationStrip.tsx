interface StudioVariationStripProps {
  variations: Array<{ id: string; title: string; subtitle: string }>;
  selected: string | null;
  onSelect: (id: string) => void;
}

export function StudioVariationStrip({ variations, selected, onSelect }: StudioVariationStripProps) {
  return (
    <div>
      <p className="mb-2 text-xs uppercase tracking-[0.18em] text-slate-400">Variacoes e historico</p>
      <div className="flex gap-2 overflow-x-auto pb-1">
        {variations.map((variation) => (
          <button
            key={variation.id}
            onClick={() => onSelect(variation.id)}
            type="button"
            className={`min-w-44 rounded-xl border px-3 py-2 text-left ${selected === variation.id ? 'border-cyan-300/50 bg-cyan-400/15 text-cyan-100' : 'border-white/10 bg-white/5 text-slate-200'}`}
          >
            <p className="text-sm font-semibold">{variation.title}</p>
            <p className="text-xs opacity-80">{variation.subtitle}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
