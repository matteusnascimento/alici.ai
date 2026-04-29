import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Check, Mail, Receipt, Shield, Smartphone, Sparkles, UserCircle2, Zap } from 'lucide-react';

import { getAccountProfile, logoutAccount } from '../../../services/account.service';
import { LogoutButton } from '../LogoutButton';
import { PlanCard } from '../PlanCard';
import { SettingsRow } from '../SettingsRow';
import { useAuth } from '../../../hooks/useAuth';
import { useBilling } from '../../../hooks/useBilling';
import type { AccountProfile } from '../../../types/account';

// ── Inline sub-components ─────────────────────────────────────────────────────

interface UsageBarProps {
  label: string;
  used: number;
  limit: number;
}

function UsageBar({ label, used, limit }: UsageBarProps) {
  const pct = limit > 0 ? Math.min(100, Math.round((used / limit) * 100)) : 0;
  const color = pct >= 90 ? 'bg-rose-400' : pct >= 70 ? 'bg-amber-400' : 'bg-cyan';
  const urgency = pct >= 90 ? 'CRÍTICO' : pct >= 70 ? 'AVISO' : 'OK';
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-3.5 transition hover:border-white/15 hover:bg-white/[0.07]">
      <div className="mb-2 flex items-center justify-between">
        <span className="text-xs font-medium text-slate-300 uppercase tracking-[0.1em]">{label}</span>
        <span className={`text-xs font-semibold ${pct >= 90 ? 'text-rose-300' : pct >= 70 ? 'text-amber-300' : 'text-emerald-300'}`}>
          {urgency}
        </span>
      </div>
      <div className="mb-1.5 flex items-center justify-between">
        <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-white/5">
          <div className={`h-full rounded-full transition-all duration-300 ${color}`} style={{ width: `${pct}%` }} />
        </div>
      </div>
      <div className="text-right text-xs text-slate-400">{used} / {limit} ({pct}%)</div>
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

interface StatusBadgeProps {
  status: 'ativo' | 'incompleto' | 'alerta';
  label: string;
}

function StatusBadge({ status, label }: StatusBadgeProps) {
  const colors = {
    ativo: 'bg-emerald-500/15 text-emerald-300',
    incompleto: 'bg-amber-500/15 text-amber-300',
    alerta: 'bg-rose-500/15 text-rose-300',
  };
  return <span className={`inline-block rounded-full px-2 py-1 text-xs font-semibold ${colors[status]}`}>{label}</span>;
}

// ── Main page ─────────────────────────────────────────────────────────────────

export function AccountHomePage() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const { plans, current, usage, history, loading: billingLoading, startCheckout, openPortal, cancel, resume, error: billingError } = useBilling();
  const [profile, setProfile] = useState<AccountProfile | null>(null);
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');

  const isOnFreePlan = !current || current.plan_id === 'free';
  const hasStripeBilling = Boolean(current?.stripe_customer_id && current.plan_id !== 'free');
  const usageRate = usage && Array.isArray(usage.items) && usage.items.length > 0 
    ? Math.max(...usage.items.map(item => item.limit > 0 ? Math.round((item.used / item.limit) * 100) : 0))
    : 0;
  const urgentUpgrade = usageRate >= 80;

  useEffect(() => {
    void getAccountProfile().then(setProfile).catch(() => setProfile(null));
  }, []);

  const profileCompletionChecks = [
    Boolean(profile?.avatar_url),
    Boolean(profile?.bio && profile.bio.trim().length >= 20),
    Boolean(profile?.company),
    Boolean(profile?.job_title),
    Boolean(profile?.timezone),
    Boolean(profile?.email_verified),
    Boolean(profile?.phone_verified),
  ];
  const profileCompletion = profile
    ? Math.round((profileCompletionChecks.filter(Boolean).length / profileCompletionChecks.length) * 100)
    : 0;

  function scrollToPlans() {
    document.getElementById('billing-plans')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  return (
    <div className="space-y-5">
      {/* ── ACCOUNT STATUS HERO ───────────────────────────────────────────── */}
      <section className={`rounded-3xl border p-6 transition ${
        urgentUpgrade 
          ? 'border-rose-500/40 bg-gradient-to-br from-rose-500/10 to-transparent' 
          : 'border-white/10 bg-gradient-to-br from-[#0c1a2e] to-[#091322]'
      }`}>
        <div className="space-y-5">
          {/* Header com status */}
          <div className="flex flex-col items-start justify-between gap-3 sm:flex-row sm:items-center">
            <div>
              <div className="flex items-center gap-2">
                <h1 className="font-display text-3xl text-white">{current?.plan_name ?? 'Free'}</h1>
                <StatusBadge status="ativo" label="Conta ativa" />
              </div>
              <p className="mt-1 text-sm text-slate-400">
                {current?.next_renewal_at 
                  ? `Renova em ${new Date(current.next_renewal_at).toLocaleDateString('pt-BR')}`
                  : 'Sem cobrança recorrente'
                }
              </p>
              {current?.cancel_at_period_end && (
                <p className="mt-1 text-xs text-rose-300">⚠️ Cancelamento agendado para o fim do período</p>
              )}
            </div>

            <div className="flex shrink-0 flex-wrap gap-2">
              {isOnFreePlan ? (
                <button
                  type="button"
                  onClick={scrollToPlans}
                  className="inline-flex items-center gap-2 rounded-2xl bg-cyan px-4 py-2.5 text-sm font-semibold text-ink transition hover:bg-cyan/90 hover:shadow-lg hover:shadow-cyan/20"
                >
                  <Zap size={14} /> Fazer upgrade
                </button>
              ) : hasStripeBilling ? (
                <>
                  <button
                    type="button"
                    onClick={() => void openPortal()}
                    className="rounded-2xl border border-white/20 px-4 py-2.5 text-sm font-semibold text-slate-100 transition hover:border-cyan/45 hover:bg-white/5 hover:text-cyan"
                  >
                    Gerenciar
                  </button>
                  {current?.cancel_at_period_end ? (
                    <button
                      type="button"
                      onClick={() => void resume()}
                      className="rounded-2xl border border-emerald-400/30 px-4 py-2.5 text-sm font-semibold text-emerald-300 transition hover:border-emerald-300/60 hover:bg-emerald-500/10"
                    >
                      Reativar
                    </button>
                  ) : (
                    <button
                      type="button"
                      onClick={() => void cancel()}
                      className="rounded-2xl border border-white/10 px-4 py-2.5 text-sm text-slate-400 transition hover:border-rose-400/30 hover:bg-rose-500/5 hover:text-rose-300"
                    >
                      Cancelar
                    </button>
                  )}
                </>
              ) : (
                <button
                  type="button"
                  onClick={scrollToPlans}
                  className="inline-flex items-center gap-2 rounded-2xl bg-cyan px-4 py-2.5 text-sm font-semibold text-ink transition hover:bg-cyan/90 hover:shadow-lg hover:shadow-cyan/20"
                >
                  <Zap size={14} /> Conectar billing
                </button>
              )}
            </div>
          </div>

          {/* Usage Grid */}
          {usage && Array.isArray(usage.items) && usage.items.length > 0 && (
            <div className="grid gap-2.5 sm:grid-cols-2 lg:grid-cols-3">
              {usage.items.map((item) => (
                <UsageBar key={item.metric} label={item.metric} used={item.used} limit={item.limit} />
              ))}
            </div>
          )}

          {billingError && !billingError.toLowerCase().includes('rede') && !billingError.toLowerCase().includes('network') && (
            <p className="rounded-lg border border-rose-400/30 bg-rose-500/10 px-3 py-2 text-xs text-rose-300">{billingError}</p>
          )}
        </div>
      </section>

      {/* ── UPGRADE OFFER (Se aplicável) ──────────────────────────────────── */}
      {isOnFreePlan && (
        <section className="rounded-3xl border border-cyan-500/30 bg-gradient-to-r from-cyan-500/10 to-blue-500/10 p-5">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h3 className="font-semibold text-cyan-100">Pronto para escalar?</h3>
              <p className="mt-1 text-sm text-slate-300">
                Desbloqueia agentes ilimitados, modelos avançados de IA e suporte prioritário.
              </p>
            </div>
            <button
              type="button"
              onClick={scrollToPlans}
              className="shrink-0 rounded-xl bg-cyan px-3 py-1.5 text-xs font-semibold text-ink transition hover:bg-cyan/90"
            >
              Ver planos →
            </button>
          </div>
        </section>
      )}

      {/* ── BILLING / UPGRADE ─────────────────────────────────────────────── */}
      <PlanCard
        current={current}
        plans={plans}
        billingCycle={billingCycle}
        loading={billingLoading}
        error={billingError}
        onBillingCycleChange={setBillingCycle}
        onUpgrade={(planId, cycle) => void startCheckout(planId, cycle)}
        onOpenPortal={() => void openPortal()}
      />

      {/* ── BILLING HISTORY ───────────────────────────────────────────────── */}
      {history && Array.isArray(history.events) && history.events.length > 0 && (
        <section className="rounded-3xl border border-white/10 bg-gradient-to-b from-white/[0.04] to-transparent p-5">
          <div className="mb-4 flex items-center gap-2">
            <Receipt size={16} className="text-slate-400" />
            <h2 className="font-display text-xl text-white">Histórico de cobrança</h2>
          </div>
          <div className="space-y-2">
            {history.events.slice(0, 5).map((event) => (
              <div key={event.id} className="flex items-center justify-between rounded-2xl border border-white/8 bg-white/5 px-4 py-3">
                <div className="min-w-0">
                  <p className="truncate text-sm text-slate-200">{event.description ?? event.event_type}</p>
                  <p className="mt-0.5 text-xs text-slate-500">
                    {new Date(event.created_at).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' })}
                  </p>
                </div>
                <div className="ml-4 flex shrink-0 items-center gap-3">
                  {event.amount > 0 && (
                    <span className="text-sm font-semibold text-white">
                      {event.currency} {event.amount.toFixed(2)}
                    </span>
                  )}
                  <span className={`rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-[0.12em] ${
                    event.status === 'succeeded' ? 'bg-emerald-500/15 text-emerald-300' :
                    event.status === 'failed' ? 'bg-rose-500/15 text-rose-300' :
                    'bg-slate-500/15 text-slate-300'
                  }`}>
                    {event.status ?? 'info'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="rounded-3xl border border-white/10 bg-gradient-to-b from-white/[0.04] to-transparent p-5">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div className="max-w-2xl">
            <h2 className="font-display text-xl text-white">Arquitetura da conta consolidada</h2>
            <p className="mt-2 text-sm leading-6 text-slate-300">
              A navegação principal da Conta AXI foi reduzida para um único eixo: visão geral, perfil, preferências, segurança e integrações.
              Configurações paralelas de idioma e aparência foram incorporadas ao fluxo único de preferências.
            </p>
          </div>
          <div className="grid w-full gap-3 sm:grid-cols-2 lg:max-w-xl">
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <div className="flex items-center gap-2 text-cyan">
                <Sparkles size={16} />
                <p className="text-sm font-semibold text-white">Preferências globais</p>
              </div>
              <p className="mt-2 text-xs leading-5 text-slate-400">Tema, idioma e cor passam a responder a um único estado global com persistência no backend.</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <div className="flex items-center gap-2 text-emerald-300">
                <Check size={16} />
                <p className="text-sm font-semibold text-white">Fluxo unificado</p>
              </div>
              <p className="mt-2 text-xs leading-5 text-slate-400">Idioma e aparência duplicados foram redirecionados para a mesma página de preferências.</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <div className="flex items-center gap-2 text-slate-300">
                <Shield size={16} />
                <p className="text-sm font-semibold text-white">Menos ruído</p>
              </div>
              <p className="mt-2 text-xs leading-5 text-slate-400">A tela de visão geral deixa de replicar o menu lateral como segunda navegação concorrente.</p>
            </div>
          </div>
        </div>
      </section>

      {profile ? (
        <section className="rounded-3xl border border-white/10 bg-gradient-to-b from-white/[0.04] to-transparent p-5">
          <div className="grid gap-4 lg:grid-cols-[1.2fr_1fr]">
            <div>
              <h2 className="font-display text-xl text-white">Identidade da conta</h2>
              <p className="mt-2 text-sm leading-6 text-slate-300">
                {profile.name} usa a AXI como {profile.job_title || 'perfil em configuração'}{profile.company ? ` em ${profile.company}` : ''}.
              </p>
              <div className="mt-4 grid gap-3 sm:grid-cols-2">
                <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                  <div className="flex items-center gap-2 text-slate-300"><UserCircle2 size={15} /><span className="text-xs uppercase tracking-[0.14em]">Perfil</span></div>
                  <p className="mt-2 text-sm text-white">@{profile.username}</p>
                  <p className="mt-1 text-xs text-slate-500">{profile.language} · {profile.timezone || 'Fuso pendente'}</p>
                </div>
                <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
                  <div className="flex items-center gap-2 text-slate-300"><Mail size={15} /><span className="text-xs uppercase tracking-[0.14em]">Verificação</span></div>
                  <p className="mt-2 text-sm text-white">{profile.email_verified ? 'Email validado' : 'Email pendente'}</p>
                  <p className="mt-1 text-xs text-slate-500">{profile.phone_verified ? 'Telefone validado' : 'Telefone pendente'}</p>
                </div>
              </div>
            </div>
            <div className="rounded-2xl border border-cyan/20 bg-cyan/5 p-5">
              <p className="text-xs uppercase tracking-[0.16em] text-cyan">Saúde do perfil</p>
              <p className="mt-2 font-display text-3xl text-white">{profileCompletion}%</p>
              <p className="mt-1 text-sm text-slate-300">Perfil concluído</p>
              <div className="mt-4 h-2 overflow-hidden rounded-full bg-white/10">
                <div className="h-full rounded-full bg-cyan" style={{ width: `${profileCompletion}%` }} />
              </div>
              <div className="mt-4 space-y-2 text-xs text-slate-300">
                <div className="flex items-center justify-between"><span>Empresa e cargo</span><span>{profile.company && profile.job_title ? 'OK' : 'Pendente'}</span></div>
                <div className="flex items-center justify-between"><span>Bio e avatar</span><span>{profile.bio && profile.avatar_url ? 'OK' : 'Pendente'}</span></div>
                <div className="flex items-center justify-between"><span>Verificações</span><span>{profile.email_verified && profile.phone_verified ? 'OK' : 'Pendente'}</span></div>
              </div>
            </div>
          </div>

          <div className="mt-4 grid gap-3 md:grid-cols-3">
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <div className="flex items-center gap-2 text-emerald-300"><Mail size={15} /><span className="text-xs uppercase tracking-[0.14em]">Email</span></div>
              <p className="mt-2 text-sm text-white">{profile.email_verified ? 'Verificado' : 'Ação necessária'}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <div className="flex items-center gap-2 text-amber-300"><Smartphone size={15} /><span className="text-xs uppercase tracking-[0.14em]">Telefone</span></div>
              <p className="mt-2 text-sm text-white">{profile.phone_verified ? 'Verificado' : 'Ação necessária'}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
              <div className="flex items-center gap-2 text-cyan"><Shield size={15} /><span className="text-xs uppercase tracking-[0.14em]">Último acesso</span></div>
              <p className="mt-2 text-sm text-white">{profile.last_login_at ? new Date(profile.last_login_at).toLocaleString('pt-BR') : 'Sem registro'}</p>
            </div>
          </div>
        </section>
      ) : null}

      {/* ── SESSION ───────────────────────────────────────────────────────── */}
      <section className="rounded-3xl border border-white/10 bg-gradient-to-br from-[#16111f] to-[#120f19] p-5">
        <div className="space-y-4">
          <div>
            <h3 className="font-display text-xl text-white">Sessão ativa</h3>
            <p className="mt-1 text-xs text-slate-400">Protegida por autenticação JWT. Encerre em dispositivos compartilhados.</p>
          </div>
          
          <div className="rounded-2xl border border-white/10 bg-white/5 p-3.5">
            <div className="space-y-2 text-xs text-slate-300">
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Navegador</span>
                <span className="font-medium text-white">Chrome · Windows</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400">Conectado há</span>
                <span className="font-medium text-white">Hoje, há alguns minutos</span>
              </div>
            </div>
          </div>

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

