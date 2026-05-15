import type { ChannelProviderCatalogItem } from '../../../types/agentsV2';
import { cn } from '../../../utils/cn';
import { ChannelStatusBadge } from './ChannelStatusBadge';
import { CHANNEL_VISUALS } from './channelVisuals';

interface ChannelProviderCardProps {
  item: ChannelProviderCatalogItem;
  selected: boolean;
  isLoading: boolean;
  onSelect: (provider: string) => void;
}

export function ChannelProviderCard({ item, selected, isLoading, onSelect }: ChannelProviderCardProps) {
  const visual = CHANNEL_VISUALS[item.provider] ?? CHANNEL_VISUALS.api;
  const Icon = visual.icon;
  const disabled = item.status === 'coming_soon' || !item.supports_activation;

  return (
    <button
      type="button"
      onClick={() => onSelect(item.provider)}
      disabled={disabled || isLoading}
      className={cn(
        'group relative overflow-hidden rounded-[28px] border p-5 text-left transition duration-200',
        selected
          ? 'border-cyan-300/40 bg-cyan-500/10 shadow-[0_0_0_1px_rgba(103,232,249,0.1)]'
          : 'border-white/10 bg-white/[0.04] hover:border-white/20 hover:bg-white/[0.06]',
        disabled && 'cursor-not-allowed opacity-70',
      )}
    >
      <div className={cn('absolute inset-0 bg-gradient-to-br opacity-90', visual.accent)} />
      <div className="relative flex h-full flex-col gap-4">
        <div className="flex items-start justify-between gap-3">
          <span className="inline-flex h-12 w-12 items-center justify-center rounded-2xl border border-white/12 bg-black/30 text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]">
            <Icon size={20} />
          </span>
          <ChannelStatusBadge status={item.status} />
        </div>

        <div className="space-y-2">
          <div>
            <h3 className="font-display text-lg text-white">{item.title}</h3>
            <p className="mt-1 text-sm text-slate-300">{item.description}</p>
          </div>
          <p className="text-xs leading-5 text-slate-400">{item.helper_text}</p>
        </div>

        <div className="mt-auto flex items-center justify-between gap-3 border-t border-white/10 pt-4 text-xs text-slate-300">
          <div>
            <div>{item.connected_accounts} conta(s)</div>
            <div className="text-slate-500">{item.active_bindings} vinculo(s) ativo(s)</div>
          </div>
          <span className="rounded-full border border-white/12 px-3 py-1 text-[11px] uppercase tracking-[0.16em] text-slate-200">
            {disabled ? 'Indisponivel' : 'Selecionar'}
          </span>
        </div>
      </div>
    </button>
  );
}
