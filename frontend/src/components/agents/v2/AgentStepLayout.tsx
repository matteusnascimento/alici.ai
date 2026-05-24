interface AgentStepLayoutProps {
  title: string;
  subtitle: string;
  step: number;
  total: number;
  children: React.ReactNode;
  onBack?: () => void;
  onNext?: () => void;
  nextLabel?: string;
}

export function AgentStepLayout({ title, subtitle, step, total, children, onBack, onNext, nextLabel }: AgentStepLayoutProps) {
  return (
    <section className="rounded-3xl border border-white/10 bg-[linear-gradient(160deg,rgba(7,14,32,0.95),rgba(11,25,46,0.92))] p-5">
      <p className="text-xs uppercase tracking-[0.18em] text-cyan-300">Etapa {step} de {total}</p>
      <h2 className="mt-1 font-display text-3xl text-white">{title}</h2>
      <p className="mt-1 text-sm text-slate-300">{subtitle}</p>
      <div className="mt-5">{children}</div>
      <div className="mt-6 flex items-center justify-between">
        <button type="button" onClick={onBack} disabled={!onBack} className="rounded-xl border border-white/20 px-4 py-2 text-sm text-slate-100 disabled:opacity-40">Voltar</button>
        <button type="button" onClick={onNext} disabled={!onNext} className="rounded-xl bg-cyan px-4 py-2 text-sm font-semibold text-ink disabled:opacity-50">{nextLabel || 'Continuar'}</button>
      </div>
    </section>
  );
}
