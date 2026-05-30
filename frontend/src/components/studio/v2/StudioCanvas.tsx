import { Maximize2, Play, ScanSearch, Upload, ZoomIn } from 'lucide-react';

interface StudioCanvasProps {
  title: string;
  subtitle: string;
  children?: React.ReactNode;
  onUpload?: () => void;
  showHeader?: boolean;
}

export function StudioCanvas({ title, subtitle, children, onUpload, showHeader = true }: StudioCanvasProps) {
  return (
    <section className="relative h-[560px] overflow-hidden rounded-3xl border border-white/10 bg-[radial-gradient(circle_at_16%_10%,rgba(192,38,211,0.18),transparent_34%),radial-gradient(circle_at_84%_18%,rgba(34,211,238,0.18),transparent_34%),linear-gradient(160deg,#050507,#0b1020)] p-4 shadow-[var(--studio-shadow)] sm:p-5">
      <div className="relative z-10 h-full">
        {showHeader ? (
        <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 className="font-display text-2xl font-bold text-white">{title}</h2>
            <p className="mt-1 text-sm text-slate-300">{subtitle}</p>
          </div>
          <div className="flex items-center gap-2 rounded-2xl border border-white/10 bg-black/35 p-1.5 backdrop-blur">
            {[
              { icon: Play, label: 'Play' },
              { icon: ZoomIn, label: 'Zoom' },
              { icon: ScanSearch, label: 'Fit' },
              { icon: Maximize2, label: 'Fullscreen' },
            ].map((control) => {
              const Icon = control.icon;
              return (
                <button key={control.label} type="button" className="inline-flex h-9 w-9 items-center justify-center rounded-xl text-slate-300 transition hover:bg-white/10 hover:text-white" title={control.label}>
                  <Icon size={16} />
                </button>
              );
            })}
          </div>
        </div>
        ) : null}
        <div className={`${showHeader ? 'h-[calc(100%-72px)]' : 'h-full'} rounded-[1.75rem] border border-white/12 bg-[linear-gradient(180deg,rgba(255,255,255,0.055),rgba(255,255,255,0.018))] p-3 shadow-[inset_0_1px_0_rgba(255,255,255,0.08)] backdrop-blur`}>
          {children || (
            <div className="flex h-full items-center justify-center rounded-[1.5rem] border border-dashed border-fuchsia-300/30 bg-black/35 text-center">
              <div className="max-w-sm px-6">
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-[var(--studio-gradient)] text-white shadow-[0_0_34px_rgba(192,38,211,0.35)]">
                  <Upload size={26} />
                </div>
                <p className="mt-5 font-display text-2xl font-bold text-white">Solte uma midia no canvas</p>
                <p className="mt-2 text-sm leading-6 text-slate-300">Comece com upload, template ou prompt de IA para montar a primeira cena.</p>
                {onUpload ? (
                  <button type="button" onClick={onUpload} className="mt-5 rounded-2xl bg-[var(--studio-gradient)] px-5 py-3 text-sm font-bold text-white shadow-[0_0_26px_rgba(34,211,238,0.22)]">
                    Fazer upload
                  </button>
                ) : null}
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
