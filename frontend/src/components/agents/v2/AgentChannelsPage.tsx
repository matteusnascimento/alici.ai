import { useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';

import type { ChannelProviderCatalogItem } from '../../../types/agentsV2';
import { useAgentChannels } from '../../../hooks/agentsV2/useAgentChannels';
import { CHANNEL_VISUALS } from './channelVisuals';
import { ChannelStatusBadge } from './ChannelStatusBadge';
import { ConnectChannelModal } from './ConnectChannelModal';
import { ConnectedChannelCard } from './ConnectedChannelCard';

function providerDescription(provider: string): string {
  const descriptions: Record<string, string> = {
    whatsapp: 'Conecte sua conta do WhatsApp para responder clientes automaticamente.',
    instagram: 'Responda DMs do Instagram com o agente, sem troca manual entre telas.',
    website_chat: 'Adicione o chat no seu site e deixe o agente atender visitantes em tempo real.',
    api: 'Integre sistemas internos via API para acionar o agente em fluxos customizados.',
    webhook: 'Receba eventos e automatize respostas do agente conforme gatilhos do seu produto.',
  };
  return descriptions[provider] || 'Conecte este canal para o agente trabalhar com mais alcance.';
}

function sectionByProvider(provider: string): 'service' | 'advanced' {
  if (['whatsapp', 'instagram'].includes(provider)) {
    return 'service';
  }
  return 'advanced';
}

function ProviderCard({ item, onOpen }: { item: ChannelProviderCatalogItem; onOpen: () => void }) {
  const visual = CHANNEL_VISUALS[item.provider] ?? CHANNEL_VISUALS.api;
  const Icon = visual.icon;

  return (
    <article className="group relative overflow-hidden rounded-[28px] border border-white/10 bg-white/[0.04] p-5 transition hover:-translate-y-0.5 hover:border-cyan-300/45 hover:bg-white/[0.06]">
      <div className={`pointer-events-none absolute inset-x-0 top-0 h-20 bg-gradient-to-br ${visual.accent} opacity-85`} />
      <div className="relative flex h-full flex-col gap-4">
        <div className="flex items-start justify-between gap-3">
          <span className="inline-flex h-11 w-11 items-center justify-center rounded-2xl border border-white/12 bg-black/30 text-white">
            <Icon size={18} />
          </span>
          <ChannelStatusBadge status={item.status} />
        </div>

        <div>
          <h3 className="font-display text-xl text-white">{item.title}</h3>
          <p className="mt-2 text-sm leading-6 text-slate-300">{providerDescription(item.provider)}</p>
        </div>

        <div className="mt-auto flex items-center justify-between">
          <div className="text-xs text-slate-400">
            <p>{item.connected_accounts} conta(s) conectada(s)</p>
            <p>{item.active_bindings} canal(is) ativos</p>
          </div>
          <button
            type="button"
            onClick={onOpen}
            className="rounded-xl border border-white/20 px-3 py-1.5 text-xs font-semibold text-slate-100 transition hover:border-cyan-300/45 hover:bg-cyan-400/10"
          >
            {item.status === 'connected' ? 'Gerenciar' : 'Conectar'}
          </button>
        </div>
      </div>
    </article>
  );
}

export function AgentChannelsPage() {
  const params = useParams();
  const agentId = Number(params.id || 0);
  const { providers, channels, loading, error, actionLoading, connect, disconnect, test } = useAgentChannels(agentId);

  const [modalOpen, setModalOpen] = useState(false);
  const [feedback, setFeedback] = useState<{ ok: boolean; message: string } | null>(null);

  const groupedProviders = useMemo(() => {
    const service = providers.filter((item) => sectionByProvider(item.provider) === 'service');
    const advanced = providers.filter((item) => sectionByProvider(item.provider) === 'advanced');
    return { service, advanced };
  }, [providers]);

  async function handleConnect(payload: {
    provider: string;
    integration: Record<string, unknown>;
    endpoint: Record<string, unknown>;
    fallback_enabled?: boolean;
  }) {
    try {
      await connect(payload);
      setFeedback({ ok: true, message: 'Canal conectado com sucesso.' });
    } catch (err) {
      setFeedback({ ok: false, message: err instanceof Error ? err.message : 'Falha ao conectar canal.' });
      throw err;
    }
  }

  async function handleDisconnect(bindingId: number, provider: string) {
    try {
      await disconnect(bindingId, provider);
      setFeedback({ ok: true, message: 'Canal desconectado com sucesso.' });
    } catch (err) {
      setFeedback({ ok: false, message: err instanceof Error ? err.message : 'Falha ao desconectar canal.' });
    }
  }

  async function handleTest(bindingId: number, provider: string) {
    try {
      const result = await test(bindingId, provider);
      setFeedback({ ok: result.success, message: result.message });
    } catch (err) {
      setFeedback({ ok: false, message: err instanceof Error ? err.message : 'Falha ao testar canal.' });
    }
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-44 animate-pulse rounded-[32px] bg-white/5" />
        <div className="grid gap-4 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, idx) => (
            <div key={idx} className="h-44 animate-pulse rounded-[28px] bg-white/5" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return <div className="rounded-2xl border border-rose-400/20 bg-rose-500/10 p-4 text-sm text-rose-100">{error}</div>;
  }

  return (
    <div className="space-y-6">
      <section className="rounded-[34px] border border-white/10 bg-[radial-gradient(circle_at_top_left,rgba(34,211,238,0.2),transparent_45%),linear-gradient(180deg,rgba(255,255,255,0.06),rgba(255,255,255,0.03))] p-6 shadow-[0_24px_80px_rgba(0,0,0,0.28)]">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div className="max-w-3xl">
            <h1 className="font-display text-3xl text-white md:text-4xl">Onde seu agente vai trabalhar?</h1>
            <p className="mt-3 text-sm leading-6 text-slate-300">Conecte canais para que seu agente atenda clientes automaticamente.</p>
          </div>
          <button
            type="button"
            onClick={() => setModalOpen(true)}
            className="rounded-2xl bg-cyan px-5 py-3 text-sm font-semibold text-ink transition hover:brightness-105"
          >
            Conectar canal
          </button>
        </div>
      </section>

      {feedback ? (
        <div className={`rounded-2xl border px-4 py-3 text-sm ${feedback.ok ? 'border-emerald-400/20 bg-emerald-500/10 text-emerald-100' : 'border-rose-400/20 bg-rose-500/10 text-rose-100'}`}>
          {feedback.message}
        </div>
      ) : null}

      <section className="space-y-3">
        <h2 className="font-display text-2xl text-white">Canais de atendimento</h2>
        <p className="text-sm text-slate-400">Escolha onde seu agente vai conversar com clientes no dia a dia.</p>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {groupedProviders.service.map((item) => (
            <ProviderCard key={item.provider} item={item} onOpen={() => setModalOpen(true)} />
          ))}
        </div>
      </section>

      {groupedProviders.advanced.length > 0 ? (
        <section className="space-y-3">
          <h2 className="font-display text-2xl text-white">Integrações avançadas</h2>
          <p className="text-sm text-slate-400">Conecte canais avançados disponíveis para este workspace.</p>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {groupedProviders.advanced.map((item) => (
              <ProviderCard key={item.provider} item={item} onOpen={() => setModalOpen(true)} />
            ))}
          </div>
        </section>
      ) : null}

      <section className="space-y-4">
        <div>
          <h2 className="font-display text-2xl text-white">Conexões já ativas</h2>
          <p className="text-sm text-slate-400">Acompanhe status e teste seus canais conectados.</p>
        </div>

        {channels.length > 0 ? (
          <div className="grid gap-4 xl:grid-cols-2">
            {channels.map((channel) => (
              <ConnectedChannelCard
                key={channel.binding_id}
                channel={channel}
                isLoading={Boolean(actionLoading[`binding:${channel.binding_id}`])}
                onTest={handleTest}
                onDisconnect={handleDisconnect}
              />
            ))}
          </div>
        ) : (
          <div className="rounded-[28px] border border-dashed border-white/12 bg-white/[0.03] px-6 py-10 text-center text-slate-300">
            Nenhum canal conectado ainda. Comece por WhatsApp ou Instagram.
          </div>
        )}
      </section>

      <ConnectChannelModal
        open={modalOpen}
        providers={providers}
        channels={channels}
        actionLoading={actionLoading}
        onClose={() => setModalOpen(false)}
        onConnect={handleConnect}
      />
    </div>
  );
}
