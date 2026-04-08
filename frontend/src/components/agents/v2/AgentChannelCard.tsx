import { useState } from 'react';

import type { AgentChannel } from '../../../types/agentsV2';

interface AgentChannelCardProps {
  channel: AgentChannel;
  title: string;
  description: string;
  icon?: string;
  isLoading: boolean;
  onConnect: (config?: Record<string, unknown>) => Promise<unknown>;
  onDisconnect: () => Promise<unknown>;
  onSync: () => Promise<unknown>;
  onTest: () => Promise<unknown>;
}

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
  isLoading,
  onConnect,
  onDisconnect,
  onSync,
  onTest,
}: AgentChannelCardProps) {
  const [toast, setToast] = useState<{ msg: string; ok: boolean } | null>(null);
  const [showConfig, setShowConfig] = useState(false);

  const status = channel.status || 'disconnected';
  const statusCfg = STATUS_CONFIG[status] ?? STATUS_CONFIG['disconnected'];
  const isConnected = status === 'connected';

  function showToast(msg: string, ok: boolean) {
    setToast({ msg, ok });
    setTimeout(() => setToast(null), 3500);
  }

  async function handleConnect() {
    try {
      await onConnect();
      showToast(`${title} - solicitacao de conexao enviada.`, true);
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
      await onSync();
      showToast(`${title} sincronizado.`, true);
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Falha ao sincronizar.', false);
    }
  }

  async function handleTest() {
    try {
      await onTest();
      showToast(`Teste de ${title} concluido.`, true);
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Falha no teste.', false);
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
            {isLoading ? 'Conectando...' : 'Conectar'}
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
            <p className="mt-2 rounded-xl border border-amber-400/20 bg-amber-900/20 px-3 py-2 text-xs text-amber-200">
              Para conectar, clique em <strong>Conectar</strong> apos configurar.
              As credenciais ficam armazenadas com seguranca no servidor.
            </p>
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
                onClick={() => { setShowConfig(false); void handleConnect(); }}
                className="rounded-xl bg-cyan-500 px-4 py-2 text-sm font-semibold text-black"
              >
                Conectar
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </article>
  );
}
