import {
  BarChart3,
  CheckCircle2,
  ExternalLink,
  Instagram,
  Link2,
  Loader2,
  MessageCircle,
  PlugZap,
  ShieldCheck,
  XCircle,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

import type { IntegrationAccount, IntegrationProvider } from '../../services/integrations.service';
import {
  disconnectProvider,
  listChannelIntegrations,
  listIntegrationAccounts,
  startIntegrationOAuth,
} from '../../services/integrations.service';

type NormalizedStatus = 'connected' | 'pending' | 'disconnected';

const PROVIDER_META: Record<string, { short: string; icon: React.ReactNode; accent: string; copy: string }> = {
  whatsapp: {
    short: 'WA',
    icon: <MessageCircle size={22} />,
    accent: 'from-emerald-400/20 to-cyan/10 border-emerald-300/25 text-emerald-200',
    copy: 'Login oficial da Meta para autorizar WhatsApp Business, nÃºmeros e webhooks.',
  },
  instagram: {
    short: 'IG',
    icon: <Instagram size={22} />,
    accent: 'from-pink-400/20 to-cyan/10 border-pink-300/25 text-pink-200',
    copy: 'Login oficial da Meta para autorizar Instagram profissional e DMs.',
  },
  messenger: {
    short: 'FB',
    icon: <MessageCircle size={22} />,
    accent: 'from-blue-400/20 to-cyan/10 border-blue-300/25 text-blue-200',
    copy: 'Login oficial da Meta para escolher pÃ¡ginas e ativar Messenger.',
  },
  tiktok: {
    short: 'TK',
    icon: <PlugZap size={22} />,
    accent: 'from-fuchsia-400/20 to-cyan/10 border-fuchsia-300/25 text-fuchsia-200',
    copy: 'Login TikTok Business para eventos, conta de anÃºncios e mensagens aprovadas.',
  },
  google_ads: {
    short: 'GA',
    icon: <BarChart3 size={22} />,
    accent: 'from-amber-400/20 to-cyan/10 border-amber-300/25 text-amber-100',
    copy: 'Login oficial do Google para importar metricas de anuncios, cliques e conversoes.',
  },};

function normalizeStatus(providerAccounts: IntegrationAccount[]): NormalizedStatus {
  if (providerAccounts.some((account) => account.status === 'connected' || account.status === 'active')) return 'connected';
  if (providerAccounts.some((account) => account.status === 'pending_setup' || account.status === 'auth_required')) return 'pending';
  return 'disconnected';
}

function statusUi(status: NormalizedStatus) {
  if (status === 'connected') return { label: 'Conectado', className: 'border-emerald-400/25 bg-emerald-400/10 text-emerald-300', icon: CheckCircle2 };
  if (status === 'pending') return { label: 'Configurando', className: 'border-amber-400/25 bg-amber-400/10 text-amber-300', icon: Loader2 };
  return { label: 'Desconectado', className: 'border-slate-500/25 bg-slate-500/10 text-slate-400', icon: XCircle };
}

export function IntegrationsPage() {
  const [providers, setProviders] = useState<IntegrationProvider[]>([]);
  const [accounts, setAccounts] = useState<IntegrationAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [busyProvider, setBusyProvider] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  async function reload() {
    setLoading(true);
    try {
      const [providerList, accountList] = await Promise.all([listChannelIntegrations(), listIntegrationAccounts()]);
      setProviders(Array.isArray(providerList) ? providerList : []);
      setAccounts(Array.isArray(accountList) ? accountList : []);
      setError(null);
    } catch {
      setProviders([]);
      setAccounts([]);
      setError('Nao foi possivel carregar as conexoes. Verifique sua sessao e tente novamente.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void reload();
  }, []);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const oauth = params.get('oauth');
    const provider = params.get('provider');
    if (!oauth) return;
    if (oauth === 'success') {
      setSuccess(`${provider ?? 'Canal'} conectado com sucesso. As proximas mensagens entram no atendimento omnichannel.`);
      setError(null);
      void reload();
    } else {
      setSuccess(null);
      setError(`Nao foi possivel concluir a conexao ${provider ?? ''}. Revise as permissoes no provedor e tente novamente.`);
    }
    window.history.replaceState({}, '', window.location.pathname);
  }, []);

  const totals = useMemo(() => {
    const connected = accounts.filter((account) => account.status === 'connected' || account.status === 'active').length;
    return { connected, total: providers.length };
  }, [accounts, providers]);

  async function handleOAuthConnect(provider: string) {
    setBusyProvider(provider);
    setError(null);
    setSuccess(null);
    try {
      const response = await startIntegrationOAuth(provider);
      window.location.href = response.authorization_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : `Erro ao iniciar login de ${provider}.`);
      setBusyProvider(null);
    }
  }

  async function handleDisconnect(provider: string) {
    if (!window.confirm(`Desconectar ${provider}? As novas mensagens deste canal deixam de entrar na AXI.`)) return;
    setBusyProvider(provider);
    setError(null);
    setSuccess(null);
    try {
      await disconnectProvider(provider);
      await reload();
      setSuccess(`${provider} desconectado.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : `Erro ao desconectar ${provider}.`);
    } finally {
      setBusyProvider(null);
    }
  }

  return (
    <div className="mx-auto w-full max-w-6xl space-y-6 px-4 py-6 sm:px-6">
      <section className="overflow-hidden rounded-3xl border border-white/10 bg-[radial-gradient(circle_at_0%_0%,rgba(0,212,255,0.18),transparent_38%),linear-gradient(135deg,rgba(255,255,255,0.07),rgba(255,255,255,0.025))] p-6">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-cyan/25 bg-cyan/10 px-3 py-1 text-xs font-bold uppercase tracking-[0.22em] text-cyan">
              <Link2 size={14} /> Central unica de conexoes
            </div>
            <h1 className="mt-4 font-display text-3xl font-black text-white">Conecte canais oficiais</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-300">
              O cliente autoriza cada rede com login oficial. A AXI recebe webhooks reais, organiza conversas,
              atualiza contatos e disponibiliza os dados para analise da IA.
            </p>
          </div>
          <div className="rounded-2xl border border-white/10 bg-black/20 p-4 text-sm text-slate-300">
            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Status</p>
            <p className="mt-1 text-2xl font-black text-white">{totals.connected}/{totals.total}</p>
            <p>Canais conectados</p>
          </div>
        </div>
      </section>

      {error ? <div className="rounded-2xl border border-rose-500/25 bg-rose-500/10 px-4 py-3 text-sm font-semibold text-rose-300">{error}</div> : null}
      {success ? <div className="rounded-2xl border border-emerald-500/25 bg-emerald-500/10 px-4 py-3 text-sm font-semibold text-emerald-300">{success}</div> : null}

      {loading ? (
        <div className="flex h-48 items-center justify-center rounded-3xl border border-white/10 bg-white/[0.03]">
          <Loader2 className="animate-spin text-cyan" />
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {providers.map((provider) => {
            const meta = PROVIDER_META[provider.provider] ?? PROVIDER_META.whatsapp;
            const providerAccounts = accounts.filter((account) => account.provider === provider.provider);
            const status = normalizeStatus(providerAccounts);
            const statusConfig = statusUi(status);
            const StatusIcon = statusConfig.icon;
            const busy = busyProvider === provider.provider;

            return (
              <article key={provider.provider} className={`rounded-3xl border bg-gradient-to-br ${meta.accent} p-5 shadow-[0_18px_45px_rgba(0,0,0,0.18)]`}>
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-black/25 text-white">
                      {meta.icon}
                    </div>
                    <div>
                      <h2 className="font-display text-xl font-bold text-white">{provider.title}</h2>
                      <p className="text-xs text-slate-300">{meta.copy}</p>
                    </div>
                  </div>
                  <span className={`inline-flex items-center gap-1 rounded-full border px-2.5 py-1 text-xs font-bold ${statusConfig.className}`}>
                    <StatusIcon size={12} className={status === 'pending' ? 'animate-spin' : ''} /> {statusConfig.label}
                  </span>
                </div>

                {providerAccounts.length ? (
                  <div className="mt-4 space-y-2">
                    {providerAccounts.map((account) => (
                      <div key={account.id} className="flex items-center justify-between rounded-2xl border border-white/10 bg-black/20 px-3 py-2">
                        <div>
                          <p className="text-sm font-semibold text-white">{account.external_account_name || account.external_account_id || `Conta ${account.id}`}</p>
                          <p className="text-xs text-slate-400">{account.status}</p>
                        </div>
                        <ShieldCheck size={16} className="text-cyan" />
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="mt-4 rounded-2xl border border-white/10 bg-black/15 px-3 py-3 text-sm leading-6 text-slate-300">
                    Clique em conectar para abrir o login oficial do provedor e escolher a conta que deseja autorizar.
                  </p>
                )}

                <div className="mt-5 flex flex-wrap gap-2">
                  {status === 'connected' ? (
                    <button
                      type="button"
                      onClick={() => void handleDisconnect(provider.provider)}
                      disabled={busy}
                      className="inline-flex items-center gap-2 rounded-xl border border-rose-400/25 bg-rose-500/10 px-4 py-2 text-sm font-bold text-rose-200 transition hover:bg-rose-500/20 disabled:opacity-50"
                    >
                      {busy ? <Loader2 size={15} className="animate-spin" /> : <XCircle size={15} />}
                      Desconectar
                    </button>
                  ) : (
                    <button
                      type="button"
                      onClick={() => void handleOAuthConnect(provider.provider)}
                      disabled={busy}
                      className="inline-flex items-center gap-2 rounded-xl bg-cyan px-4 py-2 text-sm font-black text-ink shadow-[0_12px_28px_rgb(var(--accent-rgb)/0.25)] transition hover:bg-white disabled:opacity-50"
                    >
                      {busy ? <Loader2 size={15} className="animate-spin" /> : <ExternalLink size={15} />}
                      Conectar com login
                    </button>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      )}
    </div>
  );
}

