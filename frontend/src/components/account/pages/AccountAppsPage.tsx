import { CheckCircle2, Globe, Instagram, Loader2, MessageCircle, Plug, XCircle } from 'lucide-react';
import { useEffect, useState } from 'react';

import {
  connectIntegration,
  disconnectProvider,
  listChannelIntegrations,
  type IntegrationProvider,
} from '../../../services/integrations.service';
import { useToast } from '../../../hooks/useToast';

const PROVIDER_META: Record<string, { icon: React.ReactNode; color: string; description: string }> = {
  whatsapp: {
    icon: <MessageCircle size={22} className="text-emerald-400" />,
    color: 'border-emerald-400/20 hover:border-emerald-400/40',
    description: 'Atendimento direto pelo WhatsApp Business. Conecte seu número e ative agentes.',
  },
  instagram: {
    icon: <Instagram size={22} className="text-pink-400" />,
    color: 'border-pink-400/20 hover:border-pink-400/40',
    description: 'Resposta automática para DMs do Instagram. Conecte sua conta profissional.',
  },
  webchat: {
    icon: <Globe size={22} className="text-cyan-400" />,
    color: 'border-cyan-400/20 hover:border-cyan-400/40',
    description: 'Widget de chat para seu site. Instale em qualquer página com uma linha de código.',
  },
};

const FALLBACK_PROVIDERS: IntegrationProvider[] = [
  {
    provider: 'whatsapp',
    title: 'WhatsApp',
    description: 'Atendimento direto pelo WhatsApp Business.',
    status: 'disconnected',
    helper_text: 'Conecte seu número para ativar agentes neste canal.',
    connected_accounts: 0,
    active_bindings: 0,
    supports_activation: true,
  },
  {
    provider: 'instagram',
    title: 'Instagram',
    description: 'Resposta automática para mensagens do Instagram.',
    status: 'disconnected',
    helper_text: 'Conecte sua conta profissional para responder DMs com IA.',
    connected_accounts: 0,
    active_bindings: 0,
    supports_activation: true,
  },
  {
    provider: 'webchat',
    title: 'Web Chat',
    description: 'Widget de chat para seu site.',
    status: 'disconnected',
    helper_text: 'Instale o widget em qualquer página com uma linha de código.',
    connected_accounts: 0,
    active_bindings: 0,
    supports_activation: true,
  },
];

function statusLabel(status: string) {
  if (status === 'connected' || status === 'active') return { label: 'Conectado', color: 'text-emerald-300', dot: 'bg-emerald-400' };
  if (status === 'pending_setup' || status === 'auth_required') return { label: 'Configurando', color: 'text-amber-300', dot: 'bg-amber-400' };
  if (status === 'error') return { label: 'Erro', color: 'text-rose-300', dot: 'bg-rose-400' };
  return { label: 'Desconectado', color: 'text-slate-400', dot: 'bg-slate-600' };
}

export function AccountAppsPage() {
  const { pushToast } = useToast();
  const [providers, setProviders] = useState<IntegrationProvider[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    listChannelIntegrations()
      .then((data) => setProviders(Array.isArray(data) && data.length > 0 ? data : FALLBACK_PROVIDERS))
      .catch(() => setProviders(FALLBACK_PROVIDERS))
      .finally(() => setLoading(false));
  }, []);

  async function handleConnect(provider: IntegrationProvider) {
    setActionLoading(provider.provider);
    try {
      await connectIntegration({ provider: provider.provider });
      setProviders((prev) =>
        prev.map((p) => p.provider === provider.provider ? { ...p, status: 'connected', connected_accounts: 1 } : p)
      );
      pushToast(`${provider.title} conectado com sucesso.`, 'success');
    } catch (err) {
      pushToast(err instanceof Error ? err.message : `Falha ao conectar ${provider.title}`, 'error');
    } finally {
      setActionLoading(null);
    }
  }

  async function handleDisconnect(provider: IntegrationProvider) {
    setActionLoading(provider.provider);
    try {
      await disconnectProvider(provider.provider);
      setProviders((prev) =>
        prev.map((p) => p.provider === provider.provider ? { ...p, status: 'disconnected', connected_accounts: 0, active_bindings: 0 } : p)
      );
      pushToast(`${provider.title} desconectado.`, 'info');
    } catch (err) {
      pushToast(err instanceof Error ? err.message : `Falha ao desconectar ${provider.title}`, 'error');
    } finally {
      setActionLoading(null);
    }
  }

  const isConnected = (p: IntegrationProvider) =>
    p.status === 'connected' || p.status === 'active' || p.connected_accounts > 0;

  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
      <div className="mb-6">
        <h2 className="font-display text-2xl text-white">Integrações e Canais</h2>
        <p className="mt-1 text-sm text-slate-400">
          Conecte canais de mensagens para que seus agentes possam atender clientes automaticamente.
        </p>
      </div>

      {loading ? (
        <div className="flex items-center gap-2 text-slate-400">
          <Loader2 size={16} className="animate-spin" /> Carregando integrações…
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {providers.map((p) => {
            const meta = PROVIDER_META[p.provider];
            const st = statusLabel(p.status);
            const busy = actionLoading === p.provider;
            const connected = isConnected(p);

            return (
              <article
                key={p.provider}
                className={`rounded-2xl border bg-[linear-gradient(160deg,rgba(7,14,32,0.95),rgba(10,24,48,0.9))] p-5 transition ${meta?.color ?? 'border-white/10 hover:border-white/20'}`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-2xl border border-white/10 bg-white/5">
                      {meta?.icon ?? <Plug size={20} className="text-slate-400" />}
                    </div>
                    <div>
                      <p className="font-semibold text-white">{p.title}</p>
                      <div className="mt-0.5 flex items-center gap-1.5">
                        <span className={`h-1.5 w-1.5 rounded-full ${st.dot}`} />
                        <span className={`text-xs ${st.color}`}>{st.label}</span>
                      </div>
                    </div>
                  </div>
                  {connected ? (
                    <CheckCircle2 size={16} className="shrink-0 text-emerald-400" />
                  ) : (
                    <XCircle size={16} className="shrink-0 text-slate-600" />
                  )}
                </div>

                <p className="mt-3 text-xs leading-relaxed text-slate-400">
                  {meta?.description ?? p.description}
                </p>

                {connected && p.active_bindings > 0 && (
                  <p className="mt-2 text-xs text-emerald-300">
                    {p.active_bindings} agente{p.active_bindings !== 1 && 's'} vinculado{p.active_bindings !== 1 && 's'}
                  </p>
                )}

                <div className="mt-4">
                  {connected ? (
                    <button
                      type="button"
                      disabled={busy}
                      onClick={() => void handleDisconnect(p)}
                      className="inline-flex items-center gap-1.5 rounded-xl border border-rose-500/30 px-3 py-2 text-xs font-semibold text-rose-300 transition hover:bg-rose-500/10 disabled:opacity-50"
                    >
                      {busy ? <Loader2 size={12} className="animate-spin" /> : <XCircle size={12} />}
                      Desconectar
                    </button>
                  ) : (
                    <button
                      type="button"
                      disabled={busy}
                      onClick={() => void handleConnect(p)}
                      className="inline-flex items-center gap-1.5 rounded-xl border border-cyan-400/30 bg-cyan-500/10 px-3 py-2 text-xs font-semibold text-cyan-200 transition hover:bg-cyan-500/20 disabled:opacity-50"
                    >
                      {busy ? <Loader2 size={12} className="animate-spin" /> : <Plug size={12} />}
                      Conectar
                    </button>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
