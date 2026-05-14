import { useState } from 'react';
import { useParams } from 'react-router-dom';

import { useAgentActions } from '../../../hooks/agentsV2/useAgentActions';
import { AgentActionCard } from './AgentActionCard';
import { AgentActionConfigModal } from './AgentActionConfigModal';

const actionsCatalog = [
  { name: 'Capturar lead', type: 'save_lead', description: 'Salva lead para acompanhamento', requirement: 'CRM opcional' },
  { name: 'Criar reserva', type: 'create_booking', description: 'Inicia fluxo de reserva', requirement: 'Agenda' },
  { name: 'Consultar disponibilidade', type: 'check_availability', description: 'Consulta agenda e horarios', requirement: 'Calendario' },
  { name: 'Enviar orcamento', type: 'send_quote', description: 'Envia proposta comercial', requirement: 'Modelo de proposta' },
  { name: 'Encaminhar para humano', type: 'transfer_human', description: 'Direciona para equipe humana', requirement: 'Canal humano' },
  { name: 'Atualizar CRM', type: 'crm_update', description: 'Atualiza dados no CRM', requirement: 'Integracao CRM' },
  { name: 'Agendar reuniao', type: 'schedule_meeting', description: 'Marca reuniao no calendario', requirement: 'Calendario' },
  { name: 'Acionar webhook', type: 'webhook_call', description: 'Envia evento via webhook', requirement: 'URL webhook' },
  { name: 'Acionar API externa', type: 'api_call', description: 'Executa chamada API externa', requirement: 'Credencial API' },
];

export function AgentActionsPage() {
  const params = useParams();
  const agentId = Number(params.id || 0);
  const { data, loading, error, save } = useAgentActions(agentId);
  const [modalAction, setModalAction] = useState<string | null>(null);

  function enabledFor(name: string) {
    return data.some((item) => item.name === name && item.enabled);
  }

  if (loading) return <p className="text-slate-300">Carregando acoes...</p>;
  if (error) return <p className="text-red-300">{error}</p>;

  return (
    <div className="space-y-4">
      <header className="rounded-3xl border border-white/10 bg-white/5 p-4">
        <h1 className="font-display text-2xl text-white">Acoes permitidas</h1>
      </header>
      <div className="grid gap-3 md:grid-cols-2">
        {actionsCatalog.map((action) => (
          <AgentActionCard
            key={action.name}
            name={action.name}
            description={action.description}
            requirement={action.requirement}
            enabled={enabledFor(action.name)}
            onToggle={() => void save({ name: action.name, action_type: action.type, enabled: !enabledFor(action.name), config: {} })}
            onConfigure={() => setModalAction(action.name)}
          />
        ))}
      </div>
      <AgentActionConfigModal
        open={Boolean(modalAction)}
        actionName={modalAction || ''}
        onClose={() => setModalAction(null)}
        onSave={(config) => {
          if (!modalAction) return;
          const action = actionsCatalog.find((item) => item.name === modalAction);
          if (!action) return;
          void save({ name: action.name, action_type: action.type, enabled: true, config });
        }}
      />
    </div>
  );
}
