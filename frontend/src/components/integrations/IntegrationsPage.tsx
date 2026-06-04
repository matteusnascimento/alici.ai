import {
  AlertCircle,
  CheckCircle2,
  Clipboard,
  Eye,
  Loader2,
  Plug,
  RefreshCw,
  Send,
  TestTube2,
  Unplug,
} from 'lucide-react';
import { type FormEvent, useEffect, useMemo, useState } from 'react';

import { ApiError } from '../../services/api';
import {
  connectProvider,
  connectProviderCredentials,
  disconnectProvider,
  getWebsiteChatScript,
  listChannelIntegrations,
  syncProvider,
  testProvider,
  testProviderCredentials,
  testWebsiteChatInstallation,
  startGoogleOAuth,
  startMetaOAuth,
  type IntegrationProvider,
  type WebsiteChatScriptResponse,
} from '../../services/integrations.service';

type ProviderKey =
  | 'whatsapp'
  | 'instagram'
  | 'website_chat'
  | 'meta_ads'
  | 'google_ads'
  | 'google_analytics'
  | 'omnibees'
  | 'pms'
  | 'stripe'
  | 'api'
  | 'webhook'
  | 'email';

interface ProviderDefinition {
  provider: ProviderKey;
  title: string;
  description: string;
}

const GROUPS: Array<{ title: string; providers: ProviderDefinition[] }> = [
  {
    title: 'Atendimento',
    providers: [
      { provider: 'whatsapp', title: 'WhatsApp Business', description: 'Mensagens, leads e atendimento oficial via Meta OAuth.' },
      { provider: 'instagram', title: 'Instagram Business', description: 'DMs, origem de leads e atendimento via Meta OAuth.' },
      { provider: 'website_chat', title: 'Chat do site', description: 'Widget AXI para capturar visitantes, eventos e mensagens.' },
    ],
  },
  {
    title: 'Marketing e anuncios',
    providers: [
      { provider: 'meta_ads', title: 'Meta Ads', description: 'Campanhas, investimento, leads e ROAS por OAuth Meta.' },
      { provider: 'google_ads', title: 'Google Ads', description: 'Campanhas, custo e conversoes por OAuth Google.' },
      { provider: 'google_analytics', title: 'Google Analytics', description: 'Trafego, eventos e conversoes do site por OAuth Google.' },
    ],
  },
  {
    title: 'Hotelaria',
    providers: [
      { provider: 'omnibees', title: 'OmniBees', description: 'Reservas, disponibilidade e dados hoteleiros por API.' },
      { provider: 'pms', title: 'PMS / Sistema hoteleiro', description: 'Reservas e hospedes vindos do sistema operacional da pousada.' },
    ],
  },
  {
    title: 'Financeiro',
    providers: [
      { provider: 'stripe', title: 'Stripe', description: 'Billing existente, assinaturas e eventos financeiros.' },
    ],
  },
  {
    title: 'Desenvolvedor',
    providers: [
      { provider: 'api', title: 'API Externa', description: 'Endpoint HTTP para sistemas internos ou produtos proprios.' },
      { provider: 'webhook', title: 'Webhook', description: 'Receba e envie eventos operacionais por URL assinada.' },
      { provider: 'email', title: 'SMTP', description: 'Servidor SMTP para emails operacionais.' },
    ],
  },
];

const META_PROVIDERS = new Set<ProviderKey>(['whatsapp', 'instagram', 'meta_ads']);
const GOOGLE_PROVIDERS = new Set<ProviderKey>(['google_ads', 'google_analytics']);
const CREDENTIAL_PROVIDERS = new Set<ProviderKey>(['omnibees', 'pms', 'api', 'webhook', 'email']);

const statusStyles: Record<string, string> = {
  connected: 'border-emerald-400/25 bg-emerald-400/10 text-emerald-100',
  pending_setup: 'border-amber-400/25 bg-amber-400/10 text-amber-100',
  auth_required: 'border-orange-400/25 bg-orange-400/10 text-orange-100',
  error: 'border-rose-400/25 bg-rose-400/10 text-rose-100',
  disconnected: 'border-slate-400/20 bg-slate-400/10 text-slate-200',
};

function statusLabel(status: string) {
  const labels: Record<string, string> = {
    connected: 'Conectado',
    pending_setup: 'Pendente',
    auth_required: 'Credencial pendente',
    disconnected: 'Desconectado',
    error: 'Erro',
  };
  return labels[status] ?? status;
}

function providerIcon(status: string) {
  if (status === 'connected') return CheckCircle2;
  if (status === 'error' || status === 'auth_required') return AlertCircle;
  return Plug;
}

function formatDate(value?: string | null) {
  if (!value) return 'Nunca';
  return new Date(value).toLocaleString('pt-BR');
}

export function IntegrationsPage() {
  const [providers, setProviders] = useState<IntegrationProvider[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [credentialProvider, setCredentialProvider] = useState<ProviderKey | null>(null);
  const [detailsProvider, setDetailsProvider] = useState<IntegrationProvider | null>(null);
  const [widgetScript, setWidgetScript] = useState<WebsiteChatScriptResponse | null>(null);
  const [form, setForm] = useState({
    endpoint: '',
    apiKey: '',
    accountName: '',
    environment: 'production',
  });

  async function refresh() {
    setLoading(true);
    try {
      setProviders(await listChannelIntegrations());
      setError(null);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Falha ao carregar integracoes.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refresh();
  }, []);

  const providerMap = useMemo(() => new Map(providers.map((item) => [item.provider, item])), [providers]);

  function providerData(definition: ProviderDefinition) {
    const backend = providerMap.get(definition.provider);
    return {
      ...definition,
      status: backend?.status ?? 'disconnected',
      helper_text: backend?.helper_text ?? 'Conecte para ativar captura de dados.',
      connected_accounts: backend?.connected_accounts ?? 0,
      active_bindings: backend?.active_bindings ?? 0,
      account_name: backend?.account_name ?? null,
      last_sync_at: backend?.last_sync_at ?? null,
      last_error: backend?.last_error ?? null,
      data_received: backend?.data_received ?? null,
      scopes: backend?.scopes ?? [],
      raw: backend,
    };
  }

  function resetForm() {
    setForm({ endpoint: '', apiKey: '', accountName: '', environment: 'production' });
  }

  async function connect(definition: ProviderDefinition) {
    const provider = definition.provider;
    setBusy(`connect:${provider}`);
    setError(null);
    setMessage(null);
    try {
      if (META_PROVIDERS.has(provider)) {
        const result = await startMetaOAuth(provider);
        window.location.href = result.authorization_url;
        return;
      }
      if (GOOGLE_PROVIDERS.has(provider)) {
        const result = await startGoogleOAuth(provider);
        window.location.href = result.authorization_url;
        return;
      }
      if (provider === 'website_chat') {
        setWidgetScript(await getWebsiteChatScript());
        return;
      }
      if (provider === 'stripe') {
        window.location.href = '/app/admin/billing';
        return;
      }
      if (CREDENTIAL_PROVIDERS.has(provider)) {
        setCredentialProvider(provider);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Nao foi possivel iniciar a conexao.');
    } finally {
      setBusy(null);
    }
  }

  async function submitCredentials(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!credentialProvider) return;
    setBusy(`credentials:${credentialProvider}`);
    setError(null);
    setMessage(null);
    try {
      if (credentialProvider === 'omnibees' || credentialProvider === 'pms') {
        await connectProviderCredentials(credentialProvider, {
          endpoint: form.endpoint,
          api_key: form.apiKey,
          token: form.apiKey,
        });
        setMessage('Conexao validada e salva.');
      } else {
        await connectProvider(credentialProvider, {
          external_account_name: form.accountName || GROUPS.flatMap((group) => group.providers).find((item) => item.provider === credentialProvider)?.title,
          access_token: form.apiKey || undefined,
          metadata: {
            config: {
              api_url: credentialProvider === 'api' ? form.endpoint : undefined,
              webhook_url: credentialProvider === 'webhook' ? form.endpoint : undefined,
              smtp_host: credentialProvider === 'email' ? form.endpoint : undefined,
              smtp_password: credentialProvider === 'email' ? form.apiKey : undefined,
              environment: form.environment,
            },
          },
        });
        setMessage('Configuracao salva para validacao externa.');
      }
      setCredentialProvider(null);
      resetForm();
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Conexao nao foi salva.');
    } finally {
      setBusy(null);
    }
  }

  async function runConnectedAction(provider: ProviderKey, action: 'sync' | 'test' | 'disconnect') {
    setBusy(`${action}:${provider}`);
    setError(null);
    setMessage(null);
    try {
      const result = action === 'disconnect'
        ? await disconnectProvider(provider)
        : action === 'sync'
          ? await syncProvider(provider)
          : await testProvider(provider);
      setMessage('message' in result ? result.message : result.helper_text);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : `Falha ao executar ${action}.`);
    } finally {
      setBusy(null);
    }
  }

  async function testCredentials() {
    if (!credentialProvider) return;
    setBusy(`test-credentials:${credentialProvider}`);
    setError(null);
    setMessage(null);
    try {
      const result = await testProviderCredentials(credentialProvider, {
        endpoint: form.endpoint,
        api_key: form.apiKey,
        token: form.apiKey,
      });
      if (result.status !== 'ok') {
        setError(result.message);
      } else {
        setMessage(result.message);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Falha ao testar credenciais.');
    } finally {
      setBusy(null);
    }
  }

  async function testWidget() {
    if (!widgetScript) return;
    setBusy('test:website_chat');
    setError(null);
    setMessage(null);
    try {
      const result = await testWebsiteChatInstallation(widgetScript.company_id);
      if (result.status === 'ok') {
        setMessage(result.message);
      } else {
        setError(result.message);
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Falha ao testar instalacao do widget.');
    } finally {
      setBusy(null);
    }
  }

  if (loading) {
    return (
      <div className="grid min-h-80 place-items-center">
        <Loader2 className="animate-spin text-violet-300" />
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-2rem)] rounded-[1.75rem] border border-white/10 bg-[radial-gradient(circle_at_8%_0%,rgba(124,58,237,0.14),transparent_30%),#050914] p-5 text-white shadow-[0_28px_100px_rgba(0,0,0,0.48)] md:p-7">
      <header className="mb-6">
        <h1 className="font-display text-4xl">Integracoes</h1>
        <p className="mt-2 max-w-2xl text-sm text-slate-300">Conecte canais e plataformas por fluxos oficiais para alimentar Revenue, Chats, Marketing e AXI Assistant.</p>
      </header>

      {error ? <p className="mb-5 rounded-2xl border border-rose-400/30 bg-rose-500/10 p-4 text-sm text-rose-100">{error}</p> : null}
      {message ? <p className="mb-5 rounded-2xl border border-emerald-400/25 bg-emerald-400/10 p-4 text-sm text-emerald-100">{message}</p> : null}

      <div className="grid gap-6">
        {GROUPS.map((group) => (
          <section key={group.title}>
            <h2 className="mb-3 text-sm font-semibold uppercase tracking-[0.18em] text-slate-400">{group.title}</h2>
            <div className="grid gap-4 xl:grid-cols-2 2xl:grid-cols-3">
              {group.providers.map((definition) => {
                const item = providerData(definition);
                const Icon = providerIcon(item.status);
                const connected = item.status === 'connected';
                return (
                  <article key={item.provider} className="flex min-h-[270px] flex-col rounded-2xl border border-white/10 bg-slate-950/60 p-5 shadow-[0_20px_60px_rgba(0,0,0,0.24)]">
                    <div className="flex items-start justify-between gap-4">
                      <span className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-violet-500/15 text-violet-100">
                        <Icon size={22} />
                      </span>
                      <span className={`rounded-full border px-3 py-1 text-xs font-semibold ${statusStyles[item.status] ?? statusStyles.disconnected}`}>
                        {statusLabel(item.status)}
                      </span>
                    </div>
                    <h3 className="mt-4 font-display text-2xl">{item.title}</h3>
                    <p className="mt-2 text-sm leading-6 text-slate-400">{item.description}</p>
                    <p className="mt-3 text-xs leading-5 text-slate-500">
                      {connected && item.account_name ? `Conectado como: ${item.account_name}` : 'Conecte para ativar captura de dados.'}
                    </p>
                    <div className="mt-4 grid gap-2 text-xs text-slate-400">
                      <p>Ultima sincronizacao: {formatDate(item.last_sync_at)}</p>
                      <p>Dados recebidos: {item.data_received ?? 0}</p>
                      <p>Permissoes: {item.scopes.length ? item.scopes.join(', ') : 'Nenhuma concedida'}</p>
                      {item.last_error ? <p className="text-rose-200">Ultimo erro: {item.last_error}</p> : null}
                    </div>
                    <div className="mt-auto grid gap-2 pt-5 sm:grid-cols-2">
                      {!connected ? (
                        <button type="button" onClick={() => connect(definition)} disabled={busy === `connect:${item.provider}`} className="inline-flex items-center justify-center gap-2 rounded-xl bg-violet-600 px-3 py-2 text-sm font-semibold text-white disabled:opacity-50 sm:col-span-2">
                          <Plug size={15} /> Conectar
                        </button>
                      ) : (
                        <>
                          <button type="button" onClick={() => runConnectedAction(item.provider, 'sync')} disabled={busy === `sync:${item.provider}`} className="inline-flex items-center justify-center gap-2 rounded-xl border border-white/10 px-3 py-2 text-sm font-semibold text-slate-200 disabled:opacity-50">
                            <RefreshCw size={15} /> Sincronizar
                          </button>
                          <button type="button" onClick={() => runConnectedAction(item.provider, 'test')} disabled={busy === `test:${item.provider}`} className="inline-flex items-center justify-center gap-2 rounded-xl border border-white/10 px-3 py-2 text-sm font-semibold text-slate-200 disabled:opacity-50">
                            <TestTube2 size={15} /> Testar
                          </button>
                          <button type="button" onClick={() => setDetailsProvider(item.raw ?? null)} className="inline-flex items-center justify-center gap-2 rounded-xl border border-white/10 px-3 py-2 text-sm font-semibold text-slate-200">
                            <Eye size={15} /> Ver detalhes
                          </button>
                          <button type="button" onClick={() => runConnectedAction(item.provider, 'disconnect')} disabled={busy === `disconnect:${item.provider}`} className="inline-flex items-center justify-center gap-2 rounded-xl border border-rose-400/20 px-3 py-2 text-sm font-semibold text-rose-100 disabled:opacity-50">
                            <Unplug size={15} /> Desconectar
                          </button>
                        </>
                      )}
                    </div>
                  </article>
                );
              })}
            </div>
          </section>
        ))}
      </div>

      {credentialProvider ? (
        <div className="fixed inset-0 z-50 grid place-items-center bg-black/60 px-4">
          <form onSubmit={submitCredentials} className="w-full max-w-lg rounded-2xl border border-white/10 bg-slate-950 p-5 shadow-[0_30px_100px_rgba(0,0,0,0.5)]">
            <h2 className="font-display text-2xl">Conectar {credentialProvider}</h2>
            <p className="mt-2 text-sm text-slate-400">Use apenas credenciais de API. Meta e Google usam OAuth oficial fora do AXI.</p>
            <div className="mt-5 grid gap-3">
              <label className="text-sm text-slate-300">
                URL da API / host
                <input required value={form.endpoint} onChange={(event) => setForm((current) => ({ ...current, endpoint: event.target.value }))} className="mt-1 h-11 w-full rounded-xl border border-white/10 bg-slate-950 px-3 text-white outline-none focus:border-violet-300" />
              </label>
              <label className="text-sm text-slate-300">
                Nome da conta
                <input value={form.accountName} onChange={(event) => setForm((current) => ({ ...current, accountName: event.target.value }))} className="mt-1 h-11 w-full rounded-xl border border-white/10 bg-slate-950 px-3 text-white outline-none focus:border-violet-300" />
              </label>
              <label className="text-sm text-slate-300">
                API key / token
                <input required type="password" value={form.apiKey} onChange={(event) => setForm((current) => ({ ...current, apiKey: event.target.value }))} className="mt-1 h-11 w-full rounded-xl border border-white/10 bg-slate-950 px-3 text-white outline-none focus:border-violet-300" />
              </label>
              <label className="text-sm text-slate-300">
                Ambiente
                <select value={form.environment} onChange={(event) => setForm((current) => ({ ...current, environment: event.target.value }))} className="mt-1 h-11 w-full rounded-xl border border-white/10 bg-slate-950 px-3 text-white outline-none focus:border-violet-300">
                  <option value="production">Producao</option>
                  <option value="sandbox">Sandbox</option>
                </select>
              </label>
            </div>
            <div className="mt-5 flex flex-wrap gap-2">
              <button type="button" onClick={testCredentials} disabled={busy === `test-credentials:${credentialProvider}`} className="inline-flex flex-1 items-center justify-center gap-2 rounded-xl border border-white/10 px-4 py-3 text-sm font-semibold text-slate-200 disabled:opacity-50">
                <TestTube2 size={15} /> Testar conexao
              </button>
              <button type="submit" disabled={busy === `credentials:${credentialProvider}`} className="inline-flex flex-1 items-center justify-center gap-2 rounded-xl bg-violet-600 px-4 py-3 text-sm font-semibold text-white disabled:opacity-50">
                <Send size={15} /> Salvar conexao
              </button>
              <button type="button" onClick={() => { setCredentialProvider(null); resetForm(); }} className="rounded-xl border border-white/10 px-4 py-3 text-sm font-semibold text-slate-300">Cancelar</button>
            </div>
          </form>
        </div>
      ) : null}

      {widgetScript ? (
        <div className="fixed inset-0 z-50 grid place-items-center bg-black/60 px-4">
          <div className="w-full max-w-2xl rounded-2xl border border-white/10 bg-slate-950 p-5 shadow-[0_30px_100px_rgba(0,0,0,0.5)]">
            <h2 className="font-display text-2xl">Instale este script no site</h2>
            <p className="mt-2 text-sm text-slate-400">O widget so sera considerado ativo depois que eventos reais chegarem ao AXI Tracker.</p>
            <pre className="mt-5 overflow-x-auto rounded-xl border border-white/10 bg-black/30 p-4 text-xs text-cyan-100">{widgetScript.script}</pre>
            <div className="mt-5 flex flex-wrap gap-2">
              <button type="button" onClick={() => navigator.clipboard.writeText(widgetScript.script)} className="inline-flex items-center gap-2 rounded-xl bg-violet-600 px-4 py-3 text-sm font-semibold text-white">
                <Clipboard size={15} /> Copiar script
              </button>
              <button type="button" onClick={testWidget} disabled={busy === 'test:website_chat'} className="inline-flex items-center gap-2 rounded-xl border border-white/10 px-4 py-3 text-sm font-semibold text-slate-200 disabled:opacity-50">
                <TestTube2 size={15} /> Testar instalacao
              </button>
              <a href="mailto:dev@seudominio.com" className="inline-flex items-center gap-2 rounded-xl border border-white/10 px-4 py-3 text-sm font-semibold text-slate-200">
                Enviar para desenvolvedor
              </a>
              <button type="button" onClick={() => setWidgetScript(null)} className="rounded-xl border border-white/10 px-4 py-3 text-sm font-semibold text-slate-300">Fechar</button>
            </div>
          </div>
        </div>
      ) : null}

      {detailsProvider ? (
        <div className="fixed inset-0 z-50 grid place-items-center bg-black/60 px-4">
          <div className="w-full max-w-lg rounded-2xl border border-white/10 bg-slate-950 p-5 shadow-[0_30px_100px_rgba(0,0,0,0.5)]">
            <h2 className="font-display text-2xl">{detailsProvider.title}</h2>
            <dl className="mt-5 grid gap-3 text-sm text-slate-300">
              <div><dt className="text-slate-500">Status</dt><dd>{statusLabel(detailsProvider.status)}</dd></div>
              <div><dt className="text-slate-500">Conta</dt><dd>{detailsProvider.account_name ?? 'Nao informado'}</dd></div>
              <div><dt className="text-slate-500">Ultima sincronizacao</dt><dd>{formatDate(detailsProvider.last_sync_at)}</dd></div>
              <div><dt className="text-slate-500">Ultimo erro</dt><dd>{detailsProvider.last_error ?? 'Nenhum'}</dd></div>
              <div><dt className="text-slate-500">Permissoes</dt><dd>{detailsProvider.scopes?.join(', ') || 'Nenhuma'}</dd></div>
            </dl>
            <button type="button" onClick={() => setDetailsProvider(null)} className="mt-5 w-full rounded-xl bg-violet-600 px-4 py-3 text-sm font-semibold text-white">Fechar</button>
          </div>
        </div>
      ) : null}
    </div>
  );
}
