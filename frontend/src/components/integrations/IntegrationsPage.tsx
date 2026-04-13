import { CheckCircle2, Link2, Loader2, PlugZap, XCircle } from 'lucide-react';
import { useEffect, useState } from 'react';
import type { IntegrationAccount, IntegrationProvider } from '../../services/integrations.service';
import {
  connectIntegration,
  disconnectProvider,
  listChannelIntegrations,
  listIntegrationAccounts,
} from '../../services/integrations.service';

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

function StatusBadge({ status }: { status: string }) {
  const connected = status === 'connected' || status === 'active';
  return (
    <span
      className={[
        'inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium',
        connected ? 'bg-green-500/15 text-green-400' : 'bg-slate-500/15 text-slate-400',
      ].join(' ')}
    >
      {connected ? <CheckCircle2 size={11} /> : <XCircle size={11} />}
      {connected ? 'Conectado' : 'Desconectado'}
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
      setProviders(p);
      setAccounts(a);
    } catch {
      setError('Erro ao carregar integrações');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { reload(); }, []);

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
    try {
      await disconnectProvider(provider);
      await reload();
    } catch {
      setError(`Erro ao desconectar ${provider}`);
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
          const isConnected = provider.connected_accounts > 0 || provider.status === 'connected';
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
                <StatusBadge status={isConnected ? 'connected' : 'disconnected'} />
              </div>

              <p className="text-xs text-slate-500">{provider.helper_text}</p>

              {providerAccounts.length > 0 && (
                <div className="space-y-2">
                  {providerAccounts.map((acc) => (
                    <div
                      key={acc.id}
                      className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 px-3 py-2"
                    >
                      <div>
                        <p className="text-xs text-white">{acc.external_account_name ?? acc.external_account_id ?? `Conta #${acc.id}`}</p>
                        <p className="text-xs text-slate-500">{acc.status}</p>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="flex gap-2">
                {isConnected ? (
                  <button
                    onClick={() => handleDisconnect(provider.provider)}
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
                <form onSubmit={(e) => handleConnect(e, provider.provider)} className="space-y-2">
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
