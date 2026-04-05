import { Outlet } from 'react-router-dom';

import { AccountHeader } from './AccountHeader';
import { SettingsRow } from './SettingsRow';

const links = [
  { to: '/app/account', label: 'Overview', description: 'Resumo da conta e atalhos' },
  { to: '/app/account/profile', label: 'Profile', description: 'Dados pessoais e avatar' },
  { to: '/app/account/personalization', label: 'Personalization', description: 'Tema, voz, preferencias' },
  { to: '/app/account/notifications', label: 'Notifications', description: 'Preferencias de notificacao' },
  { to: '/app/account/apps', label: 'Applications', description: 'Integracoes e apps conectados' },
  { to: '/app/account/data', label: 'Data Controls', description: 'Exportacao e privacidade' },
  { to: '/app/account/security', label: 'Security', description: 'Senha e seguranca da conta' },
  { to: '/app/account/chats', label: 'Archived Chats', description: 'Conversas arquivadas' },
  { to: '/app/account/language', label: 'Language & Appearance', description: 'Idioma, tema e cor' },
  { to: '/app/account/help', label: 'Help', description: 'Suporte e versao' },
  { to: '/app/account/legal', label: 'Legal', description: 'Termos e privacidade' },
];

export function AccountShell() {
  return (
    <div className="space-y-6">
      <AccountHeader title="AXI Account" subtitle="Centro completo de perfil, seguranca, preferências e dados." />
      <div className="grid gap-6 xl:grid-cols-[320px_1fr]">
        <aside className="rounded-3xl border border-white/10 bg-white/[0.03] p-3 xl:sticky xl:top-6 xl:h-[calc(100vh-8rem)] xl:overflow-auto">
          <div className="space-y-2">
            {links.map((item) => (
              <SettingsRow key={item.to} to={item.to} label={item.label} description={item.description} />
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
