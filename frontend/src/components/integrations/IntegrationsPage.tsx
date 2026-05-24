import { CheckCircle2, Link2, Loader2, PlugZap, XCircle } from 'lucide-react';
import { useEffect, useState } from 'react';
import type { IntegrationAccount, IntegrationProvider } from '../../services/integrations.service';
import {
  connectIntegration,
  disconnectProvider,
  listChannelIntegrations,
  listIntegrationAccounts,
} from '../../services/integrations.service';

const DEV = import.meta.env.DEV;

const PROVIDER_ICONS: Record<string, string> = {
  whatsapp: '💬',
  instagram: '📸',
};

const PROVIDER_FIELDS: Record<string, { key: string; label: string; type: string }[]> = {
  whatsapp: [
    { key: 'access_token', label: 'Access Token', type: 'password' },
    { key: 'external_account_id', label: 'Phone Number ID', type: 'text' },
    { key: 'external_account_name', label: 'Nome da conta', type: 'text' },
  ],
  instagram: [
    { key: 'access_token', label: 'Access Token', type: 'password' },
    { key: 'external_account_id', label: 'Instagram Account ID', type: 'text' },
    { key: 'external_account_name', label: 'Nome da conta', type: 'text' },
  ],
};

type NormalizedStatus = 'connected' | 'pending' | 'disconnected';

/**
 * Fonte única de verdade para o status de conexão de um provedor.
 * - connected: conta com status connected/active
 * - pending: conta existe mas aguarda verificação de webhook (pending_setup/auth_required)
 * - disconnected: nenhuma conta ou todas desconectadas
 */
function normalizeStatus(provider: IntegrationProvider, providerAccounts: IntegrationAccount[]): NormalizedStatus {
  const connectedAccounts = providerAccounts.filter((a) => a.status === 'connected' || a.status === 'active');
  const pendingAccounts = providerAccounts.filter((a) => a.status === 'pending_setup' || a.status === 'auth_required');

  if (DEV) {
    console.debug(`[Integrations] ${provider.provider}`, {
      provider_status: provider.status,
      accounts_total: providerAccounts.length,
      accounts_connected: connectedAccounts.length,
      accounts_pending: pendingAccounts.length,
    });
  }

  if (connectedAccounts.length > 0) return 'connected';
  if (pendingAccounts.length > 0) return 'pending';
  return 'disconnected';
}

function StatusBadge({ status }: { status: NormalizedStatus }) {
  if (status === 'connected') {
    return (
      <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium bg-green-500/15 text-green-400">
        <CheckCircle2 size={11} /> Conectado
      </span>
    );
  }
  if (status === 'pending') {
    return (
      <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium bg-yellow-500/15 text-yellow-400">
        <Loader2 size={11} className="animate-spin" /> Configurando
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium bg-slate-500/15 text-slate-400">
      <XCircle size={11} /> Desconectado
    </span>
  );
}

export function IntegrationsPage() {
  const [providers, setProviders] = useState<IntegrationProvider[]>([]);
  const [accounts, setAccounts] = useState<IntegrationAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState<string | null>(null);
  const [disconnecting, setDisconnecting] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showFormFor, setShowFormFor] = useState<string | null>(null);
  const [formValues, setFormValues] = useState<Record<string, string>>({});

  async function reload() {
    setLoading(true);
    try {
      const [p, a] = await Promise.all([listChannelIntegrations(), listIntegrationAccounts()]);
      const safeProviders = Array.isArray(p) ? p : [];
      const safeAccounts = Array.isArray(a) ? a : [];
      if (DEV) {
        console.debug('[Integrations] reload — providers:', safeProviders, 'accounts:', safeAccounts);
      }
      setProviders(safeProviders);
      setAccounts(safeAccounts);
      setError(null);
    } catch {
      setError('Erro ao carregar integrações');
      setProviders([]);
      setAccounts([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void reload(); }, []);

  async function handleConnect(e: React.FormEvent, provider: string) {
    e.preventDefault();
    setConnecting(provider);
    setError(null);
    try {
      const { access_token, external_account_id, external_account_name, ...rest } = formValues;
      await connectIntegration({
        provider,
        access_token,
        external_account_id,
        external_account_name,
        metadata: rest,
      });
      setShowFormFor(null);
      setFormValues({});
      await reload();
    } catch {
      setError(`Erro ao conectar ${provider}`);
    } finally {
      setConnecting(null);
    }
  }

  async function handleDisconnect(provider: string) {
    if (!confirm(`Desconectar ${provider}?`)) return;
    setDisconnecting(provider);
    setError(null);

    // Update otimista: marca contas do provedor como desconectadas antes do reload
    setAccounts((current) =>
      current.map((a) =>
        a.provider === provider ? { ...a, status: 'disconnected' } : a,
      ),
    );

    try {
      const result = await disconnectProvider(provider);
      if (DEV) {
        console.debug(`[Integrations] disconnect ${provider} — resposta:`, result);
      }
      await reload();
    } catch (err) {
      const msg = err instanceof Error ? err.message : `Erro ao desconectar ${provider}`;
      setError(msg);
      // Reverte o update otimista em caso de erro
      await reload();
    } finally {
      setDisconnecting(null);
    }
  }

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 size={24} className="animate-spin text-cyan" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-8 space-y-8">
      <div className="flex items-center gap-3">
        <Link2 size={20} className="text-cyan" />
        <div>
          <h1 className="text-xl font-semibold text-white">Integrações de Canal</h1>
          <p className="text-sm text-slate-400">Conecte seus canais de atendimento aos agentes AXI</p>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-400">
          {error}
        </div>
      )}

      <div className="grid gap-5 sm:grid-cols-2">
        {providers.map((provider) => {
          const icon = PROVIDER_ICONS[provider.provider] ?? '🔗';
          const providerAccounts = accounts.filter((a) => a.provider === provider.provider);
          // Fonte única de verdade — derivada das contas reais no banco
          const connStatus = normalizeStatus(provider, providerAccounts);
          const isConnected = connStatus !== 'disconnected';
          const fields = PROVIDER_FIELDS[provider.provider] ?? [];

          return (
            <div
              key={provider.provider}
              className="rounded-2xl border border-white/10 bg-white/5 p-6 space-y-4"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{icon}</span>
                  <div>
                    <p className="font-semibold text-white">{provider.title}</p>
                    <p className="text-xs text-slate-400">{provider.description}</p>
                  </div>
                </div>
                <StatusBadge status={connStatus} />
              </div>

              <p className="text-xs text-slate-500">{provider.helper_text}</p>

              {providerAccounts.length > 0 && (
                <div className="space-y-2">
                  {providerAccounts.map((acc) => {
                    const accConnected = acc.status === 'connected' || acc.status === 'active';
                    return (
                      <div
                        key={acc.id}
                        className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 px-3 py-2"
                      >
                        <div>
                          <p className="text-xs text-white">{acc.external_account_name ?? acc.external_account_id ?? `Conta #${acc.id}`}</p>
                          <p className={`text-xs ${accConnected ? 'text-green-400' : acc.status === 'pending_setup' ? 'text-yellow-400' : 'text-slate-500'}`}>
                            {accConnected ? 'ativa' : acc.status === 'pending_setup' ? 'aguardando webhook' : 'desconectada'}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              <div className="flex gap-2">
                {isConnected ? (
                  <button
                    onClick={() => void handleDisconnect(provider.provider)}
                    disabled={disconnecting === provider.provider}
                    className="flex items-center gap-1.5 rounded-xl border border-red-500/30 px-3 py-1.5 text-xs text-red-400 hover:bg-red-500/10 disabled:opacity-50"
                  >
                    {disconnecting === provider.provider ? <Loader2 size={11} className="animate-spin" /> : <XCircle size={11} />}
                    Desconectar
                  </button>
                ) : showFormFor === provider.provider ? (
                  <button
                    type="button"
                    onClick={() => setShowFormFor(null)}
                    className="rounded-xl border border-white/15 px-3 py-1.5 text-xs text-slate-400 hover:bg-white/5"
                  >
                    Cancelar
                  </button>
                ) : (
                  <button
                    onClick={() => setShowFormFor(provider.provider)}
                    className="flex items-center gap-1.5 rounded-xl bg-cyan/10 border border-cyan/30 px-3 py-1.5 text-xs text-cyan hover:bg-cyan/20"
                  >
                    <PlugZap size={11} />
                    Conectar
                  </button>
                )}
              </div>

              {showFormFor === provider.provider && fields.length > 0 && (
                <form onSubmit={(e) => void handleConnect(e, provider.provider)} className="space-y-2">
                  {fields.map((f) => (
                    <input
                      key={f.key}
                      type={f.type}
                      required={f.key === 'access_token'}
                      placeholder={f.label}
                      value={formValues[f.key] ?? ''}
                      onChange={(e) => setFormValues((prev) => ({ ...prev, [f.key]: e.target.value }))}
                      className="w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan/50"
                    />
                  ))}
                  <button
                    type="submit"
                    disabled={connecting === provider.provider}
                    className="flex items-center gap-1.5 rounded-xl bg-cyan px-4 py-2 text-xs font-semibold text-ink hover:bg-cyan/90 disabled:opacity-50"
                  >
                    {connecting === provider.provider ? <Loader2 size={11} className="animate-spin" /> : null}
                    Salvar Conexão
                  </button>
                </form>
              )}
            </div>
          );
        })}
      </div>

      {providers.length === 0 && (
        <div className="flex flex-col items-center justify-center rounded-2xl border border-white/10 bg-white/5 py-16 gap-3 text-slate-400">
          <Link2 size={32} />
          <p className="text-sm">Nenhum provedor disponível no momento.</p>
        </div>
      )}
    </div>
  );
}
