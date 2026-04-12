import type { AgentConnectedChannel } from '../../../types/agentsV2';
import { ChannelStatusBadge } from './ChannelStatusBadge';
import { CHANNEL_VISUALS } from './channelVisuals';

interface ConnectedChannelCardProps {
  channel: AgentConnectedChannel;
  isLoading: boolean;
  onTest: (bindingId: number, provider: string) => Promise<void>;
  onDisconnect: (bindingId: number, provider: string) => Promise<void>;
}

export function ConnectedChannelCard({ channel, isLoading, onTest, onDisconnect }: ConnectedChannelCardProps) {
  const visual = CHANNEL_VISUALS[channel.provider] ?? CHANNEL_VISUALS.api;
  const Icon = visual.icon;

  return (
    <article className="relative overflow-hidden rounded-[30px] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.06),rgba(255,255,255,0.03))] p-5 shadow-[0_24px_80px_rgba(0,0,0,0.25)]">
      <div className={`absolute inset-x-0 top-0 h-24 bg-gradient-to-br ${visual.accent} opacity-90`} />
      <div className="relative flex h-full flex-col gap-4">
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-center gap-3">
            <span className="inline-flex h-12 w-12 items-center justify-center rounded-2xl border border-white/12 bg-black/30 text-white">
              <Icon size={20} />
            </span>
            <div>
              <h3 className="font-display text-lg text-white">{channel.channel_name}</h3>
              <p className="text-sm text-slate-300">{channel.external_account_name || channel.provider}</p>
            </div>
          </div>
          <ChannelStatusBadge status={channel.status} />
        </div>

        <dl className="grid gap-3 text-sm text-slate-300 md:grid-cols-2">
          <div className="rounded-2xl border border-white/8 bg-black/20 px-3 py-3">
            <dt className="text-[11px] uppercase tracking-[0.16em] text-slate-500">Provider</dt>
            <dd className="mt-1 text-white">{channel.provider}</dd>
          </div>
          <div className="rounded-2xl border border-white/8 bg-black/20 px-3 py-3">
            <dt className="text-[11px] uppercase tracking-[0.16em] text-slate-500">Canal operacional</dt>
            <dd className="mt-1 text-white">{channel.phone_number_or_handle || channel.external_channel_id || 'Canal interno'}</dd>
          </div>
          <div className="rounded-2xl border border-white/8 bg-black/20 px-3 py-3">
            <dt className="text-[11px] uppercase tracking-[0.16em] text-slate-500">Webhook</dt>
            <dd className="mt-1 text-white">{channel.webhook_status}</dd>
          </div>
          <div className="rounded-2xl border border-white/8 bg-black/20 px-3 py-3">
            <dt className="text-[11px] uppercase tracking-[0.16em] text-slate-500">Ultima atualizacao</dt>
            <dd className="mt-1 text-white">{new Date(channel.updated_at).toLocaleString('pt-BR')}</dd>
          </div>
        </dl>

        {channel.last_test_message ? (
          <div className="rounded-2xl border border-white/10 bg-white/[0.03] px-3 py-3 text-sm text-slate-300">
            <div className="text-[11px] uppercase tracking-[0.16em] text-slate-500">Ultimo teste</div>
            <p className="mt-1">{channel.last_test_message}</p>
            {channel.last_test_at ? <p className="mt-1 text-xs text-slate-500">{new Date(channel.last_test_at).toLocaleString('pt-BR')}</p> : null}
          </div>
        ) : null}

        <div className="mt-auto flex flex-wrap gap-2">
          <button
            type="button"
            disabled={isLoading}
            onClick={() => void onTest(channel.binding_id, channel.provider)}
            className="inline-flex items-center rounded-2xl border border-cyan-300/25 bg-cyan-500/10 px-4 py-2 text-sm font-medium text-cyan-100 transition hover:bg-cyan-500/15 disabled:opacity-50"
          >
            {isLoading ? 'Testando...' : 'Testar vinculo'}
          </button>
          <button
            type="button"
            disabled={isLoading}
            onClick={() => void onDisconnect(channel.binding_id, channel.provider)}
            className="inline-flex items-center rounded-2xl border border-white/15 px-4 py-2 text-sm font-medium text-slate-200 transition hover:bg-white/5 disabled:opacity-50"
          >
            Desconectar
          </button>
        </div>
      </div>
    </article>
  );
}