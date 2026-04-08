import { useParams } from 'react-router-dom';

import { useAgentChannels } from '../../../hooks/agentsV2/useAgentChannels';
import { AgentChannelCard } from './AgentChannelCard';

const CHANNEL_CATALOG: Array<{ type: string; title: string; description: string; icon: string }> = [
  { type: 'whatsapp', title: 'WhatsApp', description: 'Atendimento e vendas por mensagens.', icon: 'W' },
  { type: 'instagram', title: 'Instagram', description: 'DMs e comentarios com suporte contextual.', icon: 'I' },
  { type: 'website_chat', title: 'Website Chat', description: 'Widget de chat no seu site.', icon: 'S' },
  { type: 'email', title: 'Email', description: 'Respostas em caixas de entrada monitoradas.', icon: 'E' },
  { type: 'crm', title: 'CRM', description: 'Sincronizacao de leads e atualizacoes.', icon: 'C' },
  { type: 'api', title: 'API', description: 'Integracao com seus sistemas internos.', icon: 'A' },
  { type: 'webhook', title: 'Webhook', description: 'Eventos em tempo real para automacoes.', icon: 'H' },
];

export function AgentChannelsPage() {
  const params = useParams();
  const agentId = Number(params.id || 0);
  const { data, loading, error, actionLoading, connect, disconnect, sync, test } = useAgentChannels(agentId);

  function channelFor(type: string) {
    return data.find((ch) => ch.channel_type === type);
  }

  if (loading) return <p className="text-slate-300">Carregando integracoes...</p>;
  if (error) return <p className="text-red-300">{error}</p>;

  return (
    <div className="space-y-4">
      <header className="rounded-3xl border border-white/10 bg-white/5 p-4">
        <h1 className="font-display text-2xl text-white">Configuracoes {'>'} Integracoes</h1>
        <p className="mt-1 text-sm text-slate-300">Status em tempo real via backend para cada canal.</p>
      </header>

      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {CHANNEL_CATALOG.map((catalog) => {
          const channel = channelFor(catalog.type);
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
              icon={catalog.icon}
              description={catalog.description}
              isLoading={Boolean(actionLoading[catalog.type])}
              onConnect={(config) => connect(catalog.type, config || {})}
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
