import { BarChart3, Bot, CalendarDays } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

import { getColorValue } from '../../utils/colorMap';

interface ThemePreviewProps {
  accentColor: string;
  themeMode: string;
}

const themeBackgrounds: Record<string, string> = {
  dark: 'linear-gradient(145deg,#111827,#020617)',
  'dark-premium': 'radial-gradient(circle at 18% 0%,rgba(124,58,237,0.28),transparent 36%),linear-gradient(145deg,#09090f,#020617)',
  midnight: 'radial-gradient(circle at 20% 0%,rgba(59,130,246,0.20),transparent 38%),linear-gradient(145deg,#030712,#00010a)',
  ocean: 'radial-gradient(circle at 18% 0%,rgba(14,165,233,0.22),transparent 38%),linear-gradient(145deg,#062033,#020617)',
  executive: 'linear-gradient(145deg,#111318,#05070b)',
};

const previewCards: Array<{ label: string; value: string; icon: LucideIcon }> = [
  { label: 'Receita', value: 'R$ 128k', icon: BarChart3 },
  { label: 'Calendario', value: '12 acoes', icon: CalendarDays },
  { label: 'Assistant', value: 'Pronto', icon: Bot },
];

export function ThemePreview({ accentColor, themeMode }: ThemePreviewProps) {
  const colorValue = getColorValue(accentColor);
  const background = themeBackgrounds[themeMode] ?? themeBackgrounds.dark;

  return (
    <section className="overflow-hidden rounded-[1.4rem] border border-white/10 bg-slate-950/70 p-5 shadow-[0_22px_70px_rgba(0,0,0,0.26)]">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-violet-300">Preview</p>
          <h3 className="mt-1 font-display text-2xl text-white">Interface em tempo real</h3>
        </div>
        <span className="h-4 w-4 rounded-full" style={{ backgroundColor: colorValue }} />
      </div>

      <div className="rounded-3xl border border-white/10 p-4" style={{ background }}>
        <div className="mb-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400">AXI Business Pulse</p>
            <p className="font-display text-xl text-white">Revenue</p>
          </div>
          <button type="button" className="rounded-xl px-3 py-2 text-xs font-semibold text-white" style={{ backgroundColor: colorValue }}>
            Novo plano
          </button>
        </div>

        <div className="grid gap-3 sm:grid-cols-3">
          {previewCards.map(({ label, value, icon: Icon }) => (
            <div key={label} className="rounded-2xl border border-white/10 bg-white/[0.055] p-3">
              <Icon size={18} style={{ color: colorValue }} />
              <p className="mt-3 text-xs text-slate-400">{label}</p>
              <p className="mt-1 text-sm font-semibold text-white">{value}</p>
            </div>
          ))}
        </div>

        <div className="mt-3 rounded-2xl border border-white/10 bg-white/[0.04] p-3">
          <div className="mb-2 h-2 w-24 rounded-full" style={{ backgroundColor: colorValue }} />
          <div className="h-2 w-full rounded-full bg-white/10" />
          <div className="mt-2 h-2 w-2/3 rounded-full bg-white/10" />
        </div>
      </div>
    </section>
  );
}
