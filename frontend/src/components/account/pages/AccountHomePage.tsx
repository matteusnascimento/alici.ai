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
    <div className="space-y-4">
      <ProfileCard profile={profile} onEdit={() => navigate('/app/account/profile')} />
      <PlanCard current={subscription} plans={plans} onUpgrade={(planId) => navigate('/app/account/profile', { state: { upgradePlanId: planId } })} />

      <div className="grid gap-4 xl:grid-cols-2">
        <SettingsGroup title="Preferences">
          <SettingsRow to="/app/account/personalization" label="Personalization" description="Tema, idioma, voz, comportamento" />
          <SettingsRow to="/app/account/notifications" label="Notifications" description="Email, push, product updates" />
          <SettingsRow to="/app/account/language" label="Language & Appearance" description="Idioma, modo e accent" />
        </SettingsGroup>

        <SettingsGroup title="Privacy & Safety">
          <SettingsRow to="/app/account/data" label="Data Controls" description="Exportar dados e solicitacao de exclusao" />
          <SettingsRow to="/app/account/security" label="Security" description="Senha e status de seguranca" />
          <SettingsRow to="/app/account/chats" label="Archived Chats" description="Controle de conversas arquivadas" />
        </SettingsGroup>

        <SettingsGroup title="Support">
          <SettingsRow to="/app/account/help" label="Help" description="Central de ajuda e report bug" />
          <SettingsRow to="/app/account/legal" label="Legal" description="Termos e politica de privacidade" />
          <SettingsRow to="/app/account/apps" label="Applications" description="Integracoes e conexoes" />
        </SettingsGroup>

        <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
          <h2 className="font-display text-2xl text-white">Session</h2>
          <p className="mt-2 text-sm text-slate-300">Encerrar sessao atual de forma segura.</p>
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
