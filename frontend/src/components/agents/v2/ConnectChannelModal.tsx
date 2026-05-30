import { useEffect, useMemo, useState } from 'react';
import { ExternalLink, Loader2, QrCode, RefreshCw } from 'lucide-react';
import type { ChannelProviderCatalogItem, AgentConnectedChannel, ChannelIntegrationAccount } from '../../../types/agentsV2';
import { startChannelProviderOAuth, startWhatsAppChannelQr } from '../../../services/agentsV2.service';
import { ChannelProviderCard } from './ChannelProviderCard';
import { ChannelStatusBadge } from './ChannelStatusBadge';

interface ConnectChannelModalProps {
  open: boolean;
  initialProvider?: string | null;
  providers: ChannelProviderCatalogItem[];
  accounts: ChannelIntegrationAccount[];
  channels: AgentConnectedChannel[];
  actionLoading: Record<string, boolean>;
  onClose: () => void;
  onConnect: (payload: {
    provider: string;
    integration: Record<string, unknown>;
    endpoint: Record<string, unknown>;
    fallback_enabled?: boolean;
  }) => Promise<void>;
}

const DEFAULT_FORM: Record<string, string> = {
  external_account_name: '',
  external_account_id: '',
  access_token: '',
  external_channel_id: '',
  channel_name: '',
  phone_number_or_handle: '',
  api_url: '',
  api_key: '',
  site_url: '',
  webhook_url: '',
  secret: '',
  smtp_host: '',
  smtp_port: '',
  smtp_user: '',
  smtp_password: '',
  smtp_tls: 'true',
  smtp_ssl: '',
};

const OFFICIAL_LOGIN_PROVIDERS = new Set(['instagram']);
const QR_CODE_PROVIDERS = new Set(['whatsapp']);

interface QrSession {
  qr_code_url: string;
  pairing_code: string;
  expires_at: string;
}

type FieldTarget = 'integration' | 'endpoint' | 'config';

interface ProviderFormField {
  key: string;
  label: string;
  placeholder: string;
  target: FieldTarget;
  type?: string;
  required?: boolean;
}

const PROVIDER_FORM_FIELDS: Record<string, ProviderFormField[]> = {
  whatsapp: [],
  instagram: [],
  website_chat: [
    { key: 'channel_name', label: 'Nome do widget', placeholder: 'Chat do site principal', target: 'endpoint', required: true },
    { key: 'site_url', label: 'URL do site', placeholder: 'https://suaempresa.com', target: 'config' },
  ],
  api: [
    { key: 'channel_name', label: 'Nome da integracao', placeholder: 'API do produto', target: 'endpoint', required: true },
    { key: 'api_url', label: 'URL da API', placeholder: 'https://api.suaempresa.com/axi', target: 'config', required: true },
    { key: 'api_key', label: 'Token ou API key', placeholder: 'Opcional para Authorization Bearer', target: 'config', type: 'password' },
  ],
  email: [
    { key: 'channel_name', label: 'Nome da caixa', placeholder: 'Email de atendimento', target: 'endpoint', required: true },
    { key: 'smtp_host', label: 'SMTP host', placeholder: 'smtp.suaempresa.com', target: 'config', required: true },
    { key: 'smtp_port', label: 'SMTP porta', placeholder: '587', target: 'config', required: true },
    { key: 'smtp_user', label: 'Usuario SMTP', placeholder: 'atendimento@suaempresa.com', target: 'config', required: true },
    { key: 'smtp_password', label: 'Senha SMTP', placeholder: 'Senha ou app password', target: 'config', type: 'password', required: true },
    { key: 'smtp_tls', label: 'Usar TLS', placeholder: 'true ou false', target: 'config' },
    { key: 'smtp_ssl', label: 'Usar SSL', placeholder: 'true ou false', target: 'config' },
  ],
  webhook: [
    { key: 'channel_name', label: 'Nome do webhook', placeholder: 'Eventos comerciais', target: 'endpoint', required: true },
    { key: 'webhook_url', label: 'URL do webhook', placeholder: 'https://hooks.suaempresa.com/axi', target: 'config', required: true },
    { key: 'secret', label: 'Segredo', placeholder: 'Opcional para assinatura X-AXI-Webhook-Secret', target: 'config', type: 'password' },
  ],
};

export function ConnectChannelModal({ open, initialProvider, providers, accounts, channels, actionLoading, onClose, onConnect }: ConnectChannelModalProps) {
  const activatableProviders = useMemo(() => providers.filter((item) => item.supports_activation), [providers]);
  const [selectedProvider, setSelectedProvider] = useState<string | null>(null);
  const [form, setForm] = useState<Record<string, string>>(DEFAULT_FORM);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [qrSession, setQrSession] = useState<QrSession | null>(null);
  const [qrLoading, setQrLoading] = useState(false);

  useEffect(() => {
    if (!open) {
      setFeedback(null);
      setForm(DEFAULT_FORM);
      setSelectedProvider(null);
      setQrSession(null);
      return;
    }

    if (initialProvider && activatableProviders.some((item) => item.provider === initialProvider)) {
      setSelectedProvider(initialProvider);
      return;
    }

    setSelectedProvider(null);
  }, [open, activatableProviders, initialProvider]);

  if (!open) {
    return null;
  }

  const selected = selectedProvider ? providers.find((item) => item.provider === selectedProvider) : null;
  const providerAccounts = selected ? accounts.filter((account) => account.provider === selected.provider) : [];
  const isLoading = selected ? Boolean(actionLoading[`provider:${selected.provider}`]) : false;
  const isOfficialLoginProvider = selected ? OFFICIAL_LOGIN_PROVIDERS.has(selected.provider) : false;
  const isQrCodeProvider = selected ? QR_CODE_PROVIDERS.has(selected.provider) : false;
  const selectedFields = selected ? PROVIDER_FORM_FIELDS[selected.provider] ?? PROVIDER_FORM_FIELDS.api : [];

  function handleProviderSelect(provider: string) {
    setSelectedProvider((current) => {
      const next = current === provider ? null : provider;
      if (next !== current) {
        setForm(DEFAULT_FORM);
      }
      return next;
    });
    setFeedback(null);
    setQrSession(null);
  }

  function applyAccount(account: ChannelIntegrationAccount) {
    setForm((current) => ({
      ...current,
      external_account_id: account.external_account_id || current.external_account_id,
      external_account_name: account.external_account_name || current.external_account_name,
    }));
  }

  async function handleSubmit() {
    if (!selected) return;
    setFeedback(null);
    try {
      const config = selectedFields
        .filter((field) => field.target === 'config')
        .reduce<Record<string, string>>((payload, field) => {
          if (form[field.key]) {
            payload[field.key] = form[field.key];
          }
          return payload;
        }, {});
      const accountName =
        form.external_account_name ||
        form.smtp_user ||
        form.api_url ||
        form.webhook_url ||
        form.site_url ||
        selected.title;
      const accountId =
        form.external_account_id ||
        form.api_url ||
        form.webhook_url ||
        form.site_url ||
        form.smtp_user ||
        selected.provider;
      const channelName = form.channel_name || selected.title;

      await onConnect({
        provider: selected.provider,
        integration: {
          external_account_name: accountName,
          external_account_id: accountId,
          access_token: form.access_token || undefined,
          metadata: { source: 'agent_connect_modal', config },
        },
        endpoint: {
          external_channel_id: form.external_channel_id || undefined,
          channel_name: channelName,
          phone_number_or_handle: form.phone_number_or_handle || undefined,
        },
      });
      onClose();
      setForm(DEFAULT_FORM);
    } catch (error) {
      setFeedback(error instanceof Error ? error.message : 'Falha ao conectar canal.');
    }
  }

  async function handleOfficialLogin() {
    if (!selected) return;
    setFeedback(null);
    try {
      const result = await startChannelProviderOAuth(selected.provider, window.location.pathname);
      window.location.assign(result.authorization_url);
    } catch (error) {
      setFeedback(error instanceof Error ? error.message : 'Falha ao abrir o login oficial.');
    }
  }

  async function handleQrStart() {
    if (!selected) return;
    setFeedback(null);
    setQrLoading(true);
    try {
      const result = await startWhatsAppChannelQr(window.location.pathname);
      setQrSession({
        qr_code_url: result.qr_code_url,
        pairing_code: result.pairing_code,
        expires_at: result.expires_at,
      });
    } catch (error) {
      setFeedback(error instanceof Error ? error.message : 'Falha ao gerar QR Code.');
    } finally {
      setQrLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm">
      <div className="max-h-[92vh] w-full max-w-6xl overflow-hidden rounded-[34px] border border-white/12 bg-[#090b12] shadow-[0_30px_120px_rgba(0,0,0,0.45)]">
        <div className="grid max-h-[92vh] overflow-y-auto lg:grid-cols-[1.1fr_0.9fr]">
          <div className="border-b border-white/10 p-6 lg:border-b-0 lg:border-r">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.22em] text-cyan-200/70">Conectar canal</p>
                <h2 className="mt-2 font-display text-3xl text-white">Escolha por onde o agente vai atender</h2>
                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
                  Selecione um canal, preencha os dados da conta e vincule ao agente. Você pode conectar vários canais ao mesmo agente.
                </p>
              </div>
              <button type="button" onClick={onClose} className="rounded-2xl border border-white/12 px-4 py-2 text-sm text-slate-200 transition hover:bg-white/5">
                Fechar
              </button>
            </div>

            <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              {providers.map((item) => (
                <ChannelProviderCard
                  key={item.provider}
                  item={item}
                  selected={selected?.provider === item.provider}
                  isLoading={Boolean(actionLoading[`provider:${item.provider}`])}
                  onSelect={handleProviderSelect}
                />
              ))}
            </div>

            <div className="mt-6 rounded-[28px] border border-white/10 bg-white/[0.03] p-5">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <h3 className="text-lg font-semibold text-white">Canais já vinculados</h3>
                  <p className="mt-1 text-sm text-slate-400">Estes canais já estão ativos neste agente.</p>
                </div>
                <span className="rounded-full border border-white/12 px-3 py-1 text-xs text-slate-300">{channels.length} vínculo(s)</span>
              </div>
              <div className="mt-4 grid gap-3 md:grid-cols-2">
                {channels.length > 0 ? (
                  channels.slice(0, 4).map((channel) => (
                    <div key={channel.binding_id} className="rounded-2xl border border-white/8 bg-black/20 px-4 py-3">
                      <div className="flex items-center justify-between gap-3">
                        <div>
                          <p className="text-sm font-medium text-white">{channel.channel_name}</p>
                          <p className="text-xs text-slate-400">{channel.external_account_name || channel.provider}</p>
                        </div>
                        <ChannelStatusBadge status={channel.status} />
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="rounded-2xl border border-dashed border-white/12 bg-black/20 px-4 py-6 text-sm text-slate-400">
                    Nenhum canal vinculado ainda. Use o painel ao lado para criar o primeiro vínculo.
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="p-6">
            {selected ? (
              <div className="space-y-5">
                <div className="rounded-[28px] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.06),rgba(255,255,255,0.03))] p-5">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <h3 className="font-display text-2xl text-white">Vincular {selected.title}</h3>
                      <p className="mt-2 text-sm leading-6 text-slate-400">{selected.helper_text}</p>
                    </div>
                    <ChannelStatusBadge status={selected.status} />
                  </div>
                </div>

                <div className="hidden">
                  {providerAccounts.length > 0 ? (
                    <div className="rounded-2xl border border-cyan-300/20 bg-cyan-500/8 p-3">
                      <p className="text-xs uppercase tracking-[0.16em] text-cyan-100/80">Contas disponíveis — clique para pré-preencher</p>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {providerAccounts.slice(0, 4).map((account) => (
                          <button
                            key={account.id}
                            type="button"
                            onClick={() => applyAccount(account)}
                            className="rounded-xl border border-cyan-300/30 bg-black/20 px-3 py-1.5 text-xs text-cyan-100 transition hover:bg-cyan-500/15"
                          >
                            {account.external_account_name || account.external_account_id || `Conta ${account.id}`}
                          </button>
                        ))}
                      </div>
                    </div>
                  ) : null}

                  <label className="block">
                    <span className="mb-2 block text-xs uppercase tracking-[0.16em] text-slate-400">Nome da conta</span>
                    <input
                      value={form.external_account_name}
                      onChange={(event) => setForm((current) => ({ ...current, external_account_name: event.target.value }))}
                      placeholder={selected.provider === 'instagram' ? 'Perfil AXI no Instagram' : 'Conta AXI no WhatsApp'}
                      className="w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white outline-none transition focus:border-cyan-300/40"
                    />
                  </label>

                  <label className="block">
                    <span className="mb-2 block text-xs uppercase tracking-[0.16em] text-slate-400">ID oficial da conta</span>
                    <input
                      value={form.external_account_id}
                      onChange={(event) => setForm((current) => ({ ...current, external_account_id: event.target.value }))}
                      placeholder={selected.provider === 'instagram' ? 'instagram_account_id' : 'business_account_id'}
                      className="w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white outline-none transition focus:border-cyan-300/40"
                    />
                  </label>

                  <label className="block">
                    <span className="mb-2 block text-xs uppercase tracking-[0.16em] text-slate-400">Access token oficial</span>
                    <input
                      type="password"
                      value={form.access_token}
                      onChange={(event) => setForm((current) => ({ ...current, access_token: event.target.value }))}
                      placeholder="Opcional — necessário para ativação oficial com Meta"
                      className="w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white outline-none transition focus:border-cyan-300/40"
                    />
                  </label>

                  <label className="block">
                    <span className="mb-2 block text-xs uppercase tracking-[0.16em] text-slate-400">Nome do canal operacional</span>
                    <input
                      value={form.channel_name}
                      onChange={(event) => setForm((current) => ({ ...current, channel_name: event.target.value }))}
                      placeholder={selected.provider === 'instagram' ? 'Inbox principal' : 'Número comercial principal'}
                      className="w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white outline-none transition focus:border-cyan-300/40"
                    />
                  </label>

                  <div className="grid gap-4 md:grid-cols-2">
                    <label className="block">
                      <span className="mb-2 block text-xs uppercase tracking-[0.16em] text-slate-400">ID do endpoint</span>
                      <input
                        value={form.external_channel_id}
                        onChange={(event) => setForm((current) => ({ ...current, external_channel_id: event.target.value }))}
                        placeholder={selected.provider === 'instagram' ? 'ig_account_channel_id' : 'phone_number_id'}
                        className="w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white outline-none transition focus:border-cyan-300/40"
                      />
                    </label>

                    <label className="block">
                      <span className="mb-2 block text-xs uppercase tracking-[0.16em] text-slate-400">Numero ou handle</span>
                      <input
                        value={form.phone_number_or_handle}
                        onChange={(event) => setForm((current) => ({ ...current, phone_number_or_handle: event.target.value }))}
                        placeholder={selected.provider === 'instagram' ? '@sua_marca' : '+55 11 99999-9999'}
                        className="w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white outline-none transition focus:border-cyan-300/40"
                      />
                    </label>
                  </div>
                </div>

                {isQrCodeProvider ? (
                  <div className="space-y-4 rounded-2xl border border-emerald-300/20 bg-emerald-500/8 p-4">
                    <div className="flex items-start gap-3">
                      <span className="inline-flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl border border-emerald-300/20 bg-black/20 text-emerald-100">
                        <QrCode size={18} />
                      </span>
                      <div>
                        <h4 className="text-sm font-semibold text-white">Conectar WhatsApp com QR Code</h4>
                        <p className="mt-1 text-sm leading-6 text-emerald-50">
                          O cliente escaneia o QR Code no WhatsApp do celular. A AXI nao pede token, API key ou senha.
                        </p>
                      </div>
                    </div>

                    {qrSession ? (
                      <div className="flex flex-col gap-4 sm:flex-row sm:items-center">
                        <div className="rounded-2xl border border-white/10 bg-white p-3">
                          <img src={qrSession.qr_code_url} alt="QR Code para conectar WhatsApp" className="h-48 w-48" />
                        </div>
                        <div className="space-y-2 text-sm text-slate-200">
                          <p>Codigo: <strong className="text-white">{qrSession.pairing_code}</strong></p>
                          <p className="text-slate-400">Expira em {new Date(qrSession.expires_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}.</p>
                        </div>
                      </div>
                    ) : null}

                    <button
                      type="button"
                      disabled={qrLoading}
                      onClick={() => void handleQrStart()}
                      className="inline-flex items-center gap-2 rounded-2xl bg-cyan px-5 py-3 text-sm font-semibold text-ink transition hover:brightness-105 disabled:opacity-50"
                    >
                      {qrLoading ? <Loader2 size={16} className="animate-spin" /> : <RefreshCw size={16} />}
                      {qrSession ? 'Gerar novo QR Code' : 'Gerar QR Code'}
                    </button>
                  </div>
                ) : isOfficialLoginProvider ? (
                  <div className="space-y-4 rounded-2xl border border-cyan-300/20 bg-cyan-500/8 p-4">
                    <p className="text-sm leading-6 text-cyan-50">
                      O cliente sera levado para o login oficial do provedor. Ele usa o proprio usuario e senha, escolhe a conta autorizada e a AXI recebe apenas a autorizacao necessaria para ativar mensagens e webhooks.
                    </p>
                    <button
                      type="button"
                      disabled={isLoading}
                      onClick={() => void handleOfficialLogin()}
                      className="inline-flex items-center gap-2 rounded-2xl bg-cyan px-5 py-3 text-sm font-semibold text-ink transition hover:brightness-105 disabled:opacity-50"
                    >
                      {isLoading ? <Loader2 size={16} className="animate-spin" /> : <ExternalLink size={16} />}
                      Conectar com login oficial
                    </button>
                  </div>
                ) : (
                <div className="grid gap-4">
                  {providerAccounts.length > 0 ? (
                    <div className="rounded-2xl border border-cyan-300/20 bg-cyan-500/8 p-3">
                      <p className="text-xs uppercase tracking-[0.16em] text-cyan-100/80">Contas disponiveis - clique para pre-preencher</p>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {providerAccounts.slice(0, 4).map((account) => (
                          <button
                            key={account.id}
                            type="button"
                            onClick={() => applyAccount(account)}
                            className="rounded-xl border border-cyan-300/30 bg-black/20 px-3 py-1.5 text-xs text-cyan-100 transition hover:bg-cyan-500/15"
                          >
                            {account.external_account_name || account.external_account_id || `Conta ${account.id}`}
                          </button>
                        ))}
                      </div>
                    </div>
                  ) : null}

                  {selectedFields.map((field) => (
                    <label key={field.key} className="block">
                      <span className="mb-2 block text-xs uppercase tracking-[0.16em] text-slate-400">
                        {field.label}
                        {field.required ? <span className="text-cyan-200"> *</span> : null}
                      </span>
                      <input
                        type={field.type || 'text'}
                        required={field.required}
                        value={form[field.key] ?? ''}
                        onChange={(event) => setForm((current) => ({ ...current, [field.key]: event.target.value }))}
                        placeholder={field.placeholder}
                        className="w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white outline-none transition focus:border-cyan-300/40"
                      />
                    </label>
                  ))}
                </div>
                )}

                {!isOfficialLoginProvider && !isQrCodeProvider ? (
                <div className="rounded-2xl border border-amber-300/20 bg-amber-500/8 px-4 py-3 text-sm leading-6 text-amber-100">
                  O vínculo é real e salvo no banco. Se o token oficial ainda não estiver configurado, o canal fica salvo como <strong>pronto para ativação</strong>, sem simular conexão completa com a Meta.
                </div>

                ) : null}

                {feedback ? <div className="rounded-2xl border border-rose-400/20 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">{feedback}</div> : null}

                <div className="flex flex-wrap justify-end gap-3">
                  <button type="button" onClick={onClose} className="rounded-2xl border border-white/12 px-4 py-2.5 text-sm text-slate-200 transition hover:bg-white/5">
                    Cancelar
                  </button>
                  {!isOfficialLoginProvider && !isQrCodeProvider ? (
                  <button
                    type="button"
                    disabled={isLoading || selected.status === 'coming_soon'}
                    onClick={() => void handleSubmit()}
                    className="rounded-2xl bg-cyan px-5 py-2.5 text-sm font-semibold text-ink transition hover:brightness-105 disabled:opacity-50"
                  >
                    {isLoading ? 'Salvando...' : 'Vincular ao agente'}
                  </button>
                  ) : null}
                </div>
              </div>
            ) : (
              <div className="flex min-h-[360px] items-center justify-center rounded-[28px] border border-dashed border-white/12 bg-white/[0.03] p-6 text-center text-sm leading-6 text-slate-400">
                Selecione um canal para abrir as opcoes de vinculacao.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
