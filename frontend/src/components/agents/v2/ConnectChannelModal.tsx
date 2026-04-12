import { useEffect, useState } from 'react';
import type { ChannelProviderCatalogItem, AgentConnectedChannel } from '../../../types/agentsV2';
import { ChannelProviderCard } from './ChannelProviderCard';
import { ChannelStatusBadge } from './ChannelStatusBadge';

interface ConnectChannelModalProps {
  open: boolean;
  providers: ChannelProviderCatalogItem[];
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
};

export function ConnectChannelModal({ open, providers, channels, actionLoading, onClose, onConnect }: ConnectChannelModalProps) {
  const activatableProviders = providers.filter((item) => item.supports_activation);
  const [selectedProvider, setSelectedProvider] = useState<string>('whatsapp');
  const [form, setForm] = useState<Record<string, string>>(DEFAULT_FORM);
  const [feedback, setFeedback] = useState<string | null>(null);

  useEffect(() => {
    if (!open) {
      setFeedback(null);
      setForm(DEFAULT_FORM);
      return;
    }

    if (activatableProviders.length > 0 && !activatableProviders.some((item) => item.provider === selectedProvider)) {
      setSelectedProvider(activatableProviders[0].provider);
    }
  }, [open, activatableProviders, selectedProvider]);

  if (!open) {
    return null;
  }

  const selected = providers.find((item) => item.provider === selectedProvider) ?? activatableProviders[0] ?? providers[0];
  const isLoading = selected ? Boolean(actionLoading[`provider:${selected.provider}`]) : false;

  async function handleSubmit() {
    if (!selected) return;
    setFeedback(null);
    try {
      await onConnect({
        provider: selected.provider,
        integration: {
          external_account_name: form.external_account_name,
          external_account_id: form.external_account_id || undefined,
          access_token: form.access_token || undefined,
          metadata: { source: 'agent_connect_modal' },
        },
        endpoint: {
          external_channel_id: form.external_channel_id || undefined,
          channel_name: form.channel_name,
          phone_number_or_handle: form.phone_number_or_handle || undefined,
        },
      });
      onClose();
      setForm(DEFAULT_FORM);
    } catch (error) {
      setFeedback(error instanceof Error ? error.message : 'Falha ao conectar canal.');
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
                <h2 className="mt-2 font-display text-3xl text-white">Grid de conectividade do agente</h2>
                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
                  Escolha um provider, salve a conta real e vincule o endpoint ao agente atual. A autenticacao oficial Meta continua sinalizada com honestidade.
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
                  onSelect={setSelectedProvider}
                />
              ))}
            </div>

            <div className="mt-6 rounded-[28px] border border-white/10 bg-white/[0.03] p-5">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <h3 className="text-lg font-semibold text-white">Canais ja vinculados</h3>
                  <p className="mt-1 text-sm text-slate-400">Esses cards ja estao conectados ao agente atual e podem ser testados na tela principal.</p>
                </div>
                <span className="rounded-full border border-white/12 px-3 py-1 text-xs text-slate-300">{channels.length} vinculo(s)</span>
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
                    Nenhum canal vinculado ainda. Use o grid acima para criar o primeiro vinculo real deste agente.
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

                <div className="grid gap-4">
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
                      placeholder="Opcional agora, necessario para ativacao oficial"
                      className="w-full rounded-2xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm text-white outline-none transition focus:border-cyan-300/40"
                    />
                  </label>

                  <label className="block">
                    <span className="mb-2 block text-xs uppercase tracking-[0.16em] text-slate-400">Nome do canal operacional</span>
                    <input
                      value={form.channel_name}
                      onChange={(event) => setForm((current) => ({ ...current, channel_name: event.target.value }))}
                      placeholder={selected.provider === 'instagram' ? 'Inbox principal' : 'Numero comercial principal'}
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

                <div className="rounded-2xl border border-amber-300/20 bg-amber-500/8 px-4 py-3 text-sm leading-6 text-amber-100">
                  O vinculo e a persistencia sao reais. Se o token oficial ainda nao estiver configurado, o AXI salva tudo como pronto para ativacao oficial sem fingir conexao Meta concluida.
                </div>

                {feedback ? <div className="rounded-2xl border border-rose-400/20 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">{feedback}</div> : null}

                <div className="flex flex-wrap justify-end gap-3">
                  <button type="button" onClick={onClose} className="rounded-2xl border border-white/12 px-4 py-2.5 text-sm text-slate-200 transition hover:bg-white/5">
                    Cancelar
                  </button>
                  <button
                    type="button"
                    disabled={isLoading || selected.status === 'coming_soon'}
                    onClick={() => void handleSubmit()}
                    className="rounded-2xl bg-cyan px-5 py-2.5 text-sm font-semibold text-ink transition hover:brightness-105 disabled:opacity-50"
                  >
                    {isLoading ? 'Salvando vinculo...' : 'Salvar e vincular ao agente'}
                  </button>
                </div>
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}