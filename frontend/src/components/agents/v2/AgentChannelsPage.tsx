import { useParams } from 'react-router-dom';

import { useAgentChannels } from '../../../hooks/agentsV2/useAgentChannels';
import { AgentChannelCard } from './AgentChannelCard';

const channelCatalog = [
  { type: 'whatsapp', title: 'WhatsApp', description: 'Atendimento e vendas por mensagens instantaneas.' },
  { type: 'instagram', title: 'Instagram', description: 'DMs e comentarios com suporte contextual.' },
  { type: 'website', title: 'Website Chat', description: 'Widget de chat no seu site.' },
  { type: 'email', title: 'Email', description: 'Respostas em caixas de entrada monitoradas.' },
  { type: 'crm', title: 'CRM', description: 'Sincronizacao de leads e atualizacoes.' },
  { type: 'api', title: 'API', description: 'Integracao com seus sistemas internos.' },
  { type: 'webhook', title: 'Webhook', description: 'Eventos em tempo real para automacoes.' },
];

export function AgentChannelsPage() {
  const params = useParams();
  const agentId = Number(params.id || 0);
  const { data, loading, error, connect, reload } = useAgentChannels(agentId);

  function statusFor(type: string) {
    const found = data.find((item) => item.channel_type?.toLowerCase() === type);
    if (!found) return 'Nao conectado';
    return found.status || (found.enabled ? 'Conectado' : 'Nao conectado');
  }

  if (loading) return <p className="text-slate-300">Carregando canais...</p>;
  if (error) return <p className="text-red-300">{error}</p>;

  return (
    <div className="space-y-4">
      <header className="rounded-3xl border border-white/10 bg-white/5 p-4">
        <h1 className="font-display text-2xl text-white">Conexoes do agente</h1>
      </header>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {channelCatalog.map((channel) => (
          <AgentChannelCard
            key={channel.type}
            title={channel.title}
            description={channel.description}
            status={statusFor(channel.type)}
            onConnect={() => void connect({ channel_type: channel.type, provider_name: 'guided-connect', channel_id: `${channel.type}-${agentId}` })}
            onDisconnect={() => void reload()}
            onSync={() => void reload()}
          />
        ))}
      </div>
    </div>
  );
}
