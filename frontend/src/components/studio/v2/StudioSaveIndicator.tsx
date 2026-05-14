interface StudioSaveIndicatorProps {
  state: 'saved' | 'saving' | 'dirty';
}

export function StudioSaveIndicator({ state }: StudioSaveIndicatorProps) {
  const map = {
    saved: { label: 'Salvo', cls: 'text-emerald-300 border-emerald-400/40 bg-emerald-500/10' },
    saving: { label: 'Salvando...', cls: 'text-cyan-200 border-cyan-400/40 bg-cyan-500/10' },
    dirty: { label: 'Alteracoes pendentes', cls: 'text-amber-200 border-amber-300/40 bg-amber-500/10' },
  } as const;

  const item = map[state];

  return <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${item.cls}`}>{item.label}</span>;
}
