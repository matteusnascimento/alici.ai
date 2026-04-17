import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { logoutAccount } from '../../../services/account.service';
import { LogoutButton } from '../LogoutButton';
import { PlanCard } from '../PlanCard';
import { SettingsRow } from '../SettingsRow';
import { useAuth } from '../../../hooks/useAuth';
import { useBilling } from '../../../hooks/useBilling';

// ── Inline sub-components ─────────────────────────────────────────────────────

interface UsageBarProps {
  label: string;
  used: number;
  limit: number;
}

function UsageBar({ label, used, limit }: UsageBarProps) {
  const pct = limit > 0 ? Math.min(100, Math.round((used / limit) * 100)) : 0;
  const color = pct >= 90 ? 'bg-rose-400' : pct >= 70 ? 'bg-amber-400' : 'bg-cyan';
  return (
    <div>
      <div className="mb-1.5 flex items-center justify-between text-xs">
        <span className="text-slate-300 capitalize">{label}</span>
        <span className={pct >= 90 ? 'text-rose-300' : pct >= 70 ? 'text-amber-300' : 'text-slate-400'}>
          {used} / {limit}
        </span>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/10">
        <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

interface SettingsSectionProps {
  title: string;
  children: React.ReactNode;
}

function SettingsSection({ title, children }: SettingsSectionProps) {
  return (
    <section className="rounded-3xl border border-white/10 bg-gradient-to-b from-white/[0.04] to-transparent p-5">
      <h3 className="mb-3 text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400">{title}</h3>
      <div className="space-y-2">{children}</div>
    </section>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

export function AccountHomePage() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const { plans, current, usage, startCheckout, openPortal, cancel, resume, error: billingError } = useBilling();
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');

  const isOnFreePlan = !current || current.plan_id === 'free';

  return (
    <div className="space-y-5">
      {/* ── Plan & Usage Hero ─────────────────────────────────────────────── */}
      <section className="rounded-3xl border border-white/10 bg-gradient-to-br from-[#0c1a2e] to-[#091322] p-5 md:p-6">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-[11px] uppercase tracking-[0.22em] text-cyan/80">Plano atual</p>
            <p className="mt-2 font-display text-3xl text-white">{current?.plan_name ?? 'Free'}</p>
            {current?.next_renewal_at ? (
              <p className="mt-1 text-xs text-slate-400">
                Renova em {new Date(current.next_renewal_at).toLocaleDateString('pt-BR')}
              </p>
            ) : (
              <p className="mt-1 text-xs text-slate-400">Sem cobrança recorrente</p>
            )}
            {current?.cancel_at_period_end ? (
              <p className="mt-1.5 text-xs text-amber-300">Cancelamento agendado ao fim do período</p>
            ) : null}
          </div>

          <div className="flex shrink-0 flex-wrap gap-2">
            {isOnFreePlan ? (
              <button
                type="button"
                onClick={() => {
                  const firstPaid = plans.find((p) => p.monthly_price > 0);
                  if (firstPaid) void startCheckout(firstPaid.id, 'monthly');
                }}
                className="rounded-2xl bg-cyan px-4 py-2.5 text-sm font-semibold text-ink transition hover:bg-cyan/90"
              >
                🚀 Fazer upgrade
              </button>
            ) : (
              <>
                <button
                  type="button"
                  onClick={() => void openPortal()}
                  className="rounded-2xl border border-white/20 px-4 py-2.5 text-sm font-semibold text-slate-100 transition hover:border-cyan/45 hover:text-cyan"
                >
                  Gerenciar assinatura
                </button>
                {current?.cancel_at_period_end ? (
                  <button
                    type="button"
                    onClick={() => void resume()}
                    className="rounded-2xl border border-emerald-400/30 px-4 py-2.5 text-sm font-semibold text-emerald-300 transition hover:border-emerald-300/60"
                  >
                    Reativar
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={() => void cancel()}
                    className="rounded-2xl border border-white/10 px-4 py-2.5 text-sm text-slate-400 transition hover:border-rose-400/30 hover:text-rose-300"
                  >
                    Cancelar plano
                  </button>
                )}
              </>
            )}
          </div>
        </div>

        {usage && Array.isArray(usage.items) && usage.items.length > 0 ? (
          <div className="mt-5 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {usage.items.map((item) => (
              <UsageBar key={item.metric} label={item.metric} used={item.used} limit={item.limit} />
            ))}
          </div>
        ) : null}

        {billingError && !billingError.toLowerCase().includes('rede') && !billingError.toLowerCase().includes('network') ? (
          <p className="mt-4 text-xs text-rose-300">{billingError}</p>
        ) : null}
      </section>

      {/* ── Billing / Upgrade ────────────────────────────────────────────── */}
      <PlanCard
        current={current}
        plans={plans}
        billingCycle={billingCycle}
        onBillingCycleChange={setBillingCycle}
        onUpgrade={(planId, cycle) => void startCheckout(planId, cycle)}
        onOpenPortal={() => void openPortal()}
      />

      {/* ── Settings ─────────────────────────────────────────────────────── */}
      <div className="grid gap-4 xl:grid-cols-2">
        <SettingsSection title="Conta e perfil">
          <SettingsRow to="/app/account/profile" label="Perfil" description="Nome, foto, username e contato" />
          <SettingsRow to="/app/account/security" label="Segurança" description="Senha e status de segurança" />
          <SettingsRow to="/app/account/data-controls" label="Dados e privacidade" description="Exportar dados e solicitar exclusão" />
        </SettingsSection>

        <SettingsSection title="Preferências">
          <SettingsRow to="/app/account/personalization" label="Personalização" description="Tema, idioma, voz e comportamento" />
          <SettingsRow to="/app/account/notifications" label="Notificações" description="Email, push e atualizações do produto" />
          <SettingsRow to="/app/account/language-appearance" label="Idioma e aparência" description="Idioma, modo e accent visual" />
        </SettingsSection>

        <SettingsSection title="Integrações">
          <SettingsRow to="/app/account/applications" label="Aplicativos" description="OpenAI, WhatsApp, Instagram e conectores" />
          <SettingsRow to="/app/account/applications/status" label="Status das conexões" description="Saúde e última sincronização" />
          <SettingsRow to="/app/account/archived-chats" label="Conversas arquivadas" description="Histórico e controle de sessões" />
        </SettingsSection>

        <SettingsSection title="Suporte e legal">
          <SettingsRow to="/app/account/help" label="Central de ajuda" description="Ajuda, contatos e abertura de ticket" />
          <SettingsRow to="/app/account/help/status" label="Status da plataforma" description="Versão atual e informações operacionais" />
          <SettingsRow to="/app/account/legal" label="Legal" description="Termos de uso e política de privacidade" />
        </SettingsSection>
      </div>

      {/* ── Session ──────────────────────────────────────────────────────── */}
      <section className="rounded-3xl border border-white/10 bg-gradient-to-br from-[#16111f] to-[#120f19] p-5">
        <h3 className="font-display text-xl text-white">Sessão</h3>
        <p className="mt-1 text-sm text-slate-400">
          Sessão autenticada e protegida. Encerre quando estiver em dispositivo compartilhado.
        </p>
        <div className="mt-4">
          <LogoutButton
            onLogout={() => {
              void logoutAccount().finally(() => {
                logout();
                navigate('/login');
              });
            }}
          />
        </div>
      </section>
    </div>
  );
}

