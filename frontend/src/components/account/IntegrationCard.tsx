import type { AccountIntegration } from '../../types/account';

interface IntegrationCardProps {
  integration: AccountIntegration;
  onToggle: (enabled: boolean) => void;
}

export function IntegrationCard({ integration, onToggle }: IntegrationCardProps) {
  return (
    <article className="rounded-2xl border border-white/10 bg-ink/40 p-4">
      <div className="flex items-center justify-between">
        <div>
          <p className="font-semibold text-white">{integration.name}</p>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-300">{integration.provider}</p>
        </div>
        <span className={integration.enabled ? 'text-xs text-cyan' : 'text-xs text-slate-400'}>{integration.status}</span>
      </div>
      <button type="button" onClick={() => onToggle(!integration.enabled)} className="mt-4 rounded-xl border border-white/20 px-3 py-2 text-xs text-slate-100">
        {integration.enabled ? 'Desconectar' : 'Conectar'}
      </button>
    </article>
  );
}
