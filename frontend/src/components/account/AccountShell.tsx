import { useEffect, useState } from 'react';
import { Outlet } from 'react-router-dom';

import { getAccountProfile, getAccountSubscription } from '../../services/account.service';
import type { AccountProfile } from '../../types/account';
import type { CurrentSubscription } from '../../types/billing';
import { AccountHeader } from './AccountHeader';
import { SettingsRow } from './SettingsRow';

const sections = [
  {
    title: 'Visao geral',
    links: [
      { to: '/app/account', label: 'Overview', description: 'Central da conta e atalhos' },
      { to: '/app/account/profile', label: 'Profile', description: 'Perfil, avatar e contato' },
    ],
  },
  {
    title: 'Assinatura e preferencias',
    links: [
      { to: '/app/account/personalization', label: 'Personalization', description: 'Tema, voz e personalizacao' },
      { to: '/app/account/notifications', label: 'Notifications', description: 'Email, push e alertas' },
      { to: '/app/account/language', label: 'Language & Appearance', description: 'Idioma, modo e accent' },
    ],
  },
  {
    title: 'Seguranca e dados',
    links: [
      { to: '/app/account/security', label: 'Security', description: 'Senha e sessoes' },
      { to: '/app/account/data', label: 'Data Controls', description: 'Exportacao e privacidade' },
      { to: '/app/account/chats', label: 'Archived Chats', description: 'Conversas arquivadas' },
    ],
  },
  {
    title: 'Apps e suporte',
    links: [
      { to: '/app/account/apps', label: 'Applications', description: 'Integracoes conectadas' },
      { to: '/app/account/help', label: 'Help', description: 'Suporte e diagnostico' },
      { to: '/app/account/legal', label: 'Legal', description: 'Termos e privacidade' },
    ],
  },
];

export function AccountShell() {
  const [profile, setProfile] = useState<AccountProfile | null>(null);
  const [subscription, setSubscription] = useState<CurrentSubscription | null>(null);

  useEffect(() => {
    void Promise.all([getAccountProfile(), getAccountSubscription()])
      .then(([profileData, subscriptionData]) => {
        setProfile(profileData);
        setSubscription(subscriptionData);
      })
      .catch(() => {
        setProfile(null);
        setSubscription(null);
      });
  }, []);

  return (
    <div className="space-y-6 pb-8">
      <AccountHeader
        title="Conta AXI"
        subtitle="Gerencie perfil, assinatura, seguranca e aplicativos em um unico hub profissional."
        profile={profile}
        subscription={subscription}
      />
      <div className="grid gap-6 xl:grid-cols-[280px_minmax(0,1fr)]">
        <aside className="rounded-3xl border border-white/10 bg-gradient-to-b from-white/[0.03] to-transparent p-4 xl:sticky xl:top-6 xl:h-[calc(100vh-8rem)] xl:overflow-auto">
          <div className="space-y-5">
            {sections.map((section) => (
              <div key={section.title} className="space-y-2">
                <p className="px-1 text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-400">{section.title}</p>
                <div className="space-y-1.5">
                  {section.links.map((item) => (
                    <SettingsRow key={item.to} to={item.to} label={item.label} description={item.description} tone="navigation" />
                  ))}
                </div>
              </div>
            ))}
          </div>
        </aside>
        <div className="space-y-4">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
