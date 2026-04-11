import { useParams } from 'react-router-dom';

import { useAgentChannels } from '../../../hooks/agentsV2/useAgentChannels';
import { AgentChannelCard } from './AgentChannelCard';

const CHANNEL_CATALOG: Array<{ type: string; title: string; description: string; icon: string }> = [
  { type: 'whatsapp', title: 'WhatsApp', description: 'Atendimento e vendas por mensagens instantaneas.', icon: '💬' },
  { type: 'instagram', title: 'Instagram', description: 'DMs e comentarios com suporte contextual.', icon: '📸' },
  { type: 'website_chat', title: 'Website Chat', description: 'Widget de chat embeddavel no seu site.', icon: '🌐' },
  { type: 'email', title: 'Email', description: 'Respostas em caixas de entrada monitoradas.', icon: '📧' },
  { type: 'crm', title: 'CRM', description: 'Sincronizacao de leads e atualizacoes automatizadas.', icon: '🗂️' },
  { type: 'api', title: 'API', description: 'Integracao com seus sistemas internos via REST.', icon: '⚡' },
  { type: 'webhook', title: 'Webhook', description: 'Eventos em tempo real para automacoes externas.', icon: '🔗' },
];

export function AgentChannelsPage() {
  const params = useParams();
  const agentId = Number(params.id || 0);
  const { data, loading, error, actionLoading, connect, disconnect, sync, test } = useAgentChannels(agentId);

  function channelFor(type: string) {
    return data.find((ch) => ch.channel_type === type);
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-16 animate-pulse rounded-3xl bg-white/5" />
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {CHANNEL_CATALOG.map((catalog) => (
            <div key={catalog.type} className="h-40 animate-pulse rounded-2xl bg-white/5" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-2xl border border-rose-500/30 bg-rose-900/20 p-4 text-sm text-rose-300">
        {error}
      </div>
    );
  }

  const connectedCount = data.filter((ch) => ch.status === 'connected').length;

  return (
    <div className="space-y-4">
      <header className="rounded-3xl border border-white/10 bg-white/5 p-4">
        <h1 className="font-display text-2xl text-white">Integracoes e Canais</h1>
        <p className="mt-1 text-sm text-slate-400">
          {connectedCount} de {CHANNEL_CATALOG.length} canais conectados
        </p>
      </header>

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {CHANNEL_CATALOG.map((catalog) => {
          const channel = channelFor(catalog.type);
          const isLoading = Boolean(actionLoading[catalog.type]);
          const channelData = channel ?? {
            id: 0,
            agent_id: agentId,
            channel_type: catalog.type,
            status: 'disconnected',
            is_enabled: false,
            enabled: false,
            provider_name: 'internal',
            external_account_id: null,
            webhook_url: null,
            last_sync_at: null,
            last_error: null,
            created_at: '',
            updated_at: '',
          };

          return (
            <AgentChannelCard
              key={catalog.type}
              channel={channelData}
              title={catalog.title}
              description={catalog.description}
              icon={catalog.icon}
              isLoading={isLoading}
              onConnect={(config) => connect(catalog.type, config)}
              onDisconnect={() => disconnect(catalog.type)}
              onSync={() => sync(catalog.type)}
              onTest={() => test(catalog.type).then(() => undefined)}
            />
          );
        })}
      </div>
    </div>
  );
}
