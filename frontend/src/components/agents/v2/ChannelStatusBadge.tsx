import type { ChannelProviderStatus } from '../../../types/agentsV2';
import { cn } from '../../../utils/cn';

const STATUS_MAP: Record<ChannelProviderStatus, { label: string; classes: string }> = {
  connected: {
    label: 'Conectado',
    classes: 'border-emerald-400/30 bg-emerald-500/12 text-emerald-200',
  },
  pending_setup: {
    label: 'Em configuracao',
    classes: 'border-amber-400/30 bg-amber-500/12 text-amber-100',
  },
  auth_required: {
    label: 'Em configuracao',
    classes: 'border-orange-400/30 bg-orange-500/12 text-orange-100',
  },
  error: {
    label: 'Erro de configuracao',
    classes: 'border-rose-400/30 bg-rose-500/12 text-rose-100',
  },
  disconnected: {
    label: 'Nao conectado',
    classes: 'border-white/15 bg-white/8 text-slate-200',
  },
  coming_soon: {
    label: 'Indisponivel',
    classes: 'border-white/10 bg-white/5 text-slate-400',
  },
};

interface ChannelStatusBadgeProps {
  status: ChannelProviderStatus;
  className?: string;
}

export function ChannelStatusBadge({ status, className }: ChannelStatusBadgeProps) {
  const config = STATUS_MAP[status] ?? STATUS_MAP.disconnected;

  return (
    <span className={cn('inline-flex rounded-full border px-2.5 py-1 text-[11px] font-medium tracking-[0.02em]', config.classes, className)}>
      {config.label}
    </span>
  );
}
