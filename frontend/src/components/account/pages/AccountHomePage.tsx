import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { getAccountProfile, getAccountSubscription, logoutAccount } from '../../../services/account.service';
import { getSubscriptionPlans } from '../../../services/subscription.service';
import type { AccountProfile } from '../../../types/account';
import type { BillingPlan, CurrentSubscription } from '../../../types/billing';
import { LogoutButton } from '../LogoutButton';
import { PlanCard } from '../PlanCard';
import { ProfileCard } from '../ProfileCard';
import { SettingsGroup } from '../SettingsGroup';
import { SettingsRow } from '../SettingsRow';
import { useAuth } from '../../../hooks/useAuth';

export function AccountHomePage() {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [profile, setProfile] = useState<AccountProfile | null>(null);
  const [subscription, setSubscription] = useState<CurrentSubscription | null>(null);
  const [plans, setPlans] = useState<BillingPlan[]>([]);

  useEffect(() => {
    void Promise.all([getAccountProfile(), getAccountSubscription(), getSubscriptionPlans()]).then(([profileData, subData, plansData]) => {
      setProfile(profileData);
      setSubscription(subData);
      setPlans(plansData);
    });
  }, []);

  if (!profile) {
    return <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-5 text-slate-300">Carregando conta...</div>;
  }

  return (
    <div className="space-y-5">
      <ProfileCard profile={profile} onEdit={() => navigate('/app/account/profile')} />
      <PlanCard current={subscription} plans={plans} onUpgrade={(planId) => navigate('/app/account/profile', { state: { upgradePlanId: planId } })} />

      <div className="grid gap-4 xl:grid-cols-2">
        <SettingsGroup title="Preferencias" subtitle="Idioma, aparencia e notificacoes para uso diario.">
          <SettingsRow to="/app/account/personalization" label="Personalization" description="Tema, idioma, voz, comportamento" />
          <SettingsRow to="/app/account/notifications" label="Notifications" description="Email, push, product updates" />
          <SettingsRow to="/app/account/language" label="Language & Appearance" description="Idioma, modo e accent" />
        </SettingsGroup>

        <SettingsGroup title="Seguranca e privacidade" subtitle="Controle de acesso, dados e historico da conta.">
          <SettingsRow to="/app/account/data" label="Data Controls" description="Exportar dados e solicitacao de exclusao" />
          <SettingsRow to="/app/account/security" label="Security" description="Senha e status de seguranca" />
          <SettingsRow to="/app/account/chats" label="Archived Chats" description="Controle de conversas arquivadas" />
        </SettingsGroup>

        <SettingsGroup title="Integracoes e aplicativos" subtitle="Conecte canais e mantenha status operacional sob controle.">
          <SettingsRow to="/app/account/apps" label="Applications" description="OpenAI, WhatsApp, Instagram e conectores" />
          <SettingsRow to="/app/account/apps" label="Status das conexoes" description="Conferir saude e ultima sincronizacao" />
          <SettingsRow to="/app/account/apps" label="Acoes rapidas" description="Conectar, pausar ou desconectar provedores" />
        </SettingsGroup>

        <SettingsGroup title="Suporte e legal" subtitle="Documentacao, suporte e diretrizes da plataforma.">
          <SettingsRow to="/app/account/help" label="Help Center" description="Ajuda, contatos e abertura de ticket" />
          <SettingsRow to="/app/account/legal" label="Legal" description="Termos de uso e politica de privacidade" />
          <SettingsRow to="/app/account/help" label="Status da plataforma" description="Versao atual e informacoes operacionais" />
        </SettingsGroup>

        <section className="rounded-3xl border border-white/10 bg-gradient-to-br from-[#16111f] to-[#120f19] p-5">
          <h2 className="font-display text-2xl text-white">Sessao</h2>
          <p className="mt-2 text-sm text-slate-300">Sessao autenticada e protegida. Encerre quando estiver em dispositivo compartilhado.</p>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <div className="rounded-2xl border border-white/10 bg-black/20 px-3 py-2">
              <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Usuario ativo</p>
              <p className="mt-1 text-sm text-slate-100">{profile.email}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-black/20 px-3 py-2">
              <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Plano em uso</p>
              <p className="mt-1 text-sm text-slate-100">{subscription?.plan_name ?? profile.plan}</p>
            </div>
          </div>
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
    </div>
  );
}
