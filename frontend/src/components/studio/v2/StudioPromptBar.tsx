interface StudioPromptBarProps {
  value: string;
  onChange: (value: string) => void;
  onGenerate: () => void;
  placeholder?: string;
}

export function StudioPromptBar({ value, onChange, onGenerate, placeholder }: StudioPromptBarProps) {
  return (
    <div className="flex flex-col gap-2 rounded-2xl border border-cyan-400/20 bg-cyan-500/10 p-3 md:flex-row">
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder || 'Digite um prompt para criar com IA'}
        className="w-full rounded-xl border border-white/10 bg-black/25 px-4 py-2 text-sm text-white outline-none placeholder:text-slate-500 focus:border-cyan-300/50"
      />
      <button type="button" onClick={onGenerate} className="rounded-xl bg-cyan px-4 py-2 text-sm font-semibold text-ink hover:bg-white">
        Gerar
      </button>
    </div>
  );
}
