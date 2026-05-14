import { useState } from 'react';

import type { AgentChannel, AgentConnectionActionResult } from '../../../types/agentsV2';

interface AgentChannelCardProps {
  channel: AgentChannel;
  title: string;
  description: string;
  icon?: string;
  readiness: 'ready' | 'external-setup';
  helper: string;
  isLoading: boolean;
  onConnect: (config?: Record<string, unknown>) => Promise<AgentChannel>;
  onDisconnect: () => Promise<unknown>;
  onSync: () => Promise<AgentChannel>;
  onTest: () => Promise<AgentConnectionActionResult>;
  onSaveConfig: (payload: Record<string, unknown>) => Promise<AgentChannel>;
}

const PROVIDER_FIELDS: Record<string, Array<{ key: string; label: string; placeholder?: string; type?: string }>> = {
  whatsapp: [
    { key: 'phone_number_id', label: 'Phone Number ID' },
    { key: 'business_account_id', label: 'Business Account ID' },
    { key: 'access_token', label: 'Access Token', type: 'password' },
  ],
  instagram: [
    { key: 'instagram_account_id', label: 'Instagram Account ID' },
    { key: 'access_token', label: 'Access Token', type: 'password' },
  ],
  api: [{ key: 'api_url', label: 'API URL', placeholder: 'https://api.exemplo.com/agent' }],
  webhook: [{ key: 'webhook_url', label: 'Webhook URL', placeholder: 'https://hooks.exemplo.com/agent' }],
  email: [
    { key: 'smtp_host', label: 'SMTP Host' },
    { key: 'smtp_port', label: 'SMTP Port' },
    { key: 'smtp_user', label: 'SMTP User' },
    { key: 'smtp_password', label: 'SMTP Password', type: 'password' },
  ],
  crm: [
    { key: 'crm_type', label: 'CRM Type', placeholder: 'hubspot | salesforce | pipedrive' },
    { key: 'api_key', label: 'API Key', type: 'password' },
  ],
};

const STATUS_CONFIG: Record<string, { label: string; classes: string }> = {
  connected: { label: 'Conectado', classes: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' },
  connecting: { label: 'Conectando...', classes: 'bg-amber-500/20 text-amber-300 border-amber-500/30' },
  disconnected: { label: 'Nao conectado', classes: 'bg-slate-500/20 text-slate-400 border-slate-500/30' },
  error: { label: 'Erro', classes: 'bg-rose-500/20 text-rose-300 border-rose-500/30' },
};

export function AgentChannelCard({
  channel,
  title,
  description,
  icon,
  readiness,
  helper,
  isLoading,
  onConnect,
  onDisconnect,
  onSync,
  onTest,
  onSaveConfig,
}: AgentChannelCardProps) {
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);
  const [showConfig, setShowConfig] = useState(false);
  const [configValues, setConfigValues] = useState<Record<string, string>>({});

  const status = channel.status || 'disconnected';
  const statusCfg = STATUS_CONFIG[status] ?? STATUS_CONFIG['disconnected'];
  const isConnected = status === 'connected';
  const configFields = PROVIDER_FIELDS[channel.channel_type] ?? [];

  function showToast(msg: string, ok: boolean) {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3500);
  }

  async function handleConnect(config: Record<string, unknown> = {}) {
    try {
      const updated = await onConnect(config);
      if (updated.status === 'connected') {
        showToast(`${title} conectado com sucesso.`, true);
        return;
      }
      showToast(updated.last_error || `${title} exige configuracao externa adicional.`, false);
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Falha ao conectar.', false);
    }
  }

  async function handleDisconnect() {
    try {
      await onDisconnect();
      showToast(`${title} desconectado.`, true);
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Falha ao desconectar.', false);
    }
  }

  async function handleSync() {
    try {
      const updated = await onSync();
      if (updated.last_error) {
        showToast(updated.last_error, false);
        return;
      }
      showToast(`${title} sincronizado.`, true);
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Falha ao sincronizar.', false);
    }
  }

  async function handleTest() {
    try {
      const result = await onTest();
      showToast(result.message || `Teste de ${title} concluido.`, result.success);
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Falha no teste.', false);
    }
  }

  async function handleSaveConfigAndMaybeConnect(connectAfterSave = false) {
    try {
      const payload: Record<string, unknown> = {
        config: configValues,
        enabled: true,
      };
      if (channel.channel_type === 'webhook' && configValues.webhook_url) {
        payload.webhook_url = configValues.webhook_url;
      }
      await onSaveConfig(payload);
      if (connectAfterSave) {
        await handleConnect(configValues);
      } else {
        showToast(`Configuracao de ${title} salva.`, true);
      }
      setShowConfig(false);
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Falha ao salvar configuracao.', false);
    }
  }

  return (
    <article className="relative flex flex-col gap-3 rounded-2xl border border-white/10 bg-white/5 p-4">
      {/* Toast */}
      {toast ? (
        <div
          className={`absolute inset-x-3 top-3 z-10 rounded-xl border px-3 py-2 text-xs font-medium shadow-lg ${
            toast.ok
              ? 'border-emerald-500/40 bg-emerald-900/50 text-emerald-200'
              : 'border-rose-500/40 bg-rose-900/50 text-rose-200'
          }`}
        >
          {toast.msg}
        </div>
      ) : null}

      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          {icon ? <span className="text-lg">{icon}</span> : null}
          <div>
            <p className="font-semibold text-white">{title}</p>
            <p className="text-xs text-slate-400">{description}</p>
          </div>
        </div>
        <span className={`rounded-full border px-2 py-0.5 text-xs font-medium ${statusCfg.classes}`}>
          {statusCfg.label}
        </span>
      </div>

      {/* Meta info */}
      {channel.last_sync_at ? (
        <p className="text-xs text-slate-500">
          Ultimo sync: {new Date(channel.last_sync_at).toLocaleString('pt-BR')}
        </p>
      ) : null}
      {channel.last_error ? (
        <p className="rounded-lg border border-rose-500/20 bg-rose-900/20 px-2 py-1 text-xs text-rose-300">
          {channel.last_error}
        </p>
      ) : null}
      <div className={`rounded-xl border px-3 py-2 text-xs ${readiness === 'ready' ? 'border-emerald-500/20 bg-emerald-500/10 text-emerald-200' : 'border-amber-500/20 bg-amber-500/10 text-amber-200'}`}>
        {helper}
      </div>

      {/* Acoes */}
      <div className="flex flex-wrap gap-1.5">
        <button
          type="button"
          disabled={isLoading}
          onClick={() => setShowConfig(true)}
          className="rounded-lg border border-white/20 px-2.5 py-1 text-xs text-slate-200 hover:bg-white/10 disabled:opacity-40"
        >
          Configurar
        </button>

        {isConnected ? (
          <button
            type="button"
            disabled={isLoading}
            onClick={() => void handleDisconnect()}
            className="rounded-lg border border-rose-300/30 px-2.5 py-1 text-xs text-rose-200 hover:bg-rose-500/10 disabled:opacity-40"
          >
            {isLoading ? '...' : 'Desconectar'}
          </button>
        ) : (
          <button
            type="button"
            disabled={isLoading}
            onClick={() => void handleConnect()}
            className="rounded-lg border border-cyan-300/40 px-2.5 py-1 text-xs text-cyan-100 hover:bg-cyan-500/10 disabled:opacity-40"
          >
            {isLoading ? 'Conectando...' : readiness === 'external-setup' ? 'Configurar e conectar' : 'Conectar'}
          </button>
        )}

        <button
          type="button"
          disabled={isLoading || !isConnected}
          onClick={() => void handleSync()}
          className="rounded-lg border border-white/20 px-2.5 py-1 text-xs text-slate-200 hover:bg-white/10 disabled:opacity-40"
        >
          {isLoading ? '...' : 'Sincronizar'}
        </button>

        <button
          type="button"
          disabled={isLoading}
          onClick={() => void handleTest()}
          className="rounded-lg border border-white/20 px-2.5 py-1 text-xs text-slate-200 hover:bg-white/10 disabled:opacity-40"
        >
          Testar
        </button>
      </div>

      {/* Modal de configuracao */}
      {showConfig ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="w-full max-w-md rounded-2xl border border-white/15 bg-[#0f1117] p-5 shadow-2xl">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="font-semibold text-white">Configurar {title}</h3>
              <button
                type="button"
                onClick={() => setShowConfig(false)}
                className="text-slate-400 hover:text-white"
              >
                X
              </button>
            </div>
            <p className="text-sm text-slate-300">
              Configure as credenciais e parametros de conexao para <strong className="text-white">{title}</strong>.
            </p>
            <p className={`mt-2 rounded-xl border px-3 py-2 text-xs ${readiness === 'external-setup' ? 'border-amber-400/20 bg-amber-900/20 text-amber-200' : 'border-emerald-400/20 bg-emerald-900/20 text-emerald-200'}`}>
              {helper} As credenciais ficam armazenadas com seguranca no servidor.
            </p>
            {configFields.length > 0 ? (
              <div className="mt-4 space-y-3">
                {configFields.map((field) => (
                  <label key={field.key} className="block text-xs text-slate-300">
                    <span className="mb-1 block">{field.label}</span>
                    <input
                      type={field.type || 'text'}
                      value={configValues[field.key] || ''}
                      onChange={(event) => setConfigValues((current) => ({ ...current, [field.key]: event.target.value }))}
                      placeholder={field.placeholder}
                      className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white"
                    />
                  </label>
                ))}
              </div>
            ) : (
              <p className="mt-4 text-xs text-slate-400">Este canal nao exige credenciais externas para iniciar.</p>
            )}
            <div className="mt-4 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowConfig(false)}
                className="rounded-xl border border-white/20 px-4 py-2 text-sm text-slate-200"
              >
                Fechar
              </button>
              <button
                type="button"
                onClick={() => void handleSaveConfigAndMaybeConnect(false)}
                className="rounded-xl border border-white/20 px-4 py-2 text-sm text-slate-100"
              >
                Salvar configuracao
              </button>
              <button
                type="button"
                onClick={() => void handleSaveConfigAndMaybeConnect(true)}
                className="rounded-xl bg-cyan-500 px-4 py-2 text-sm font-semibold text-black"
              >
                Salvar e conectar
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </article>
  );
}
