import { Archive, Bell, Database, Menu, Palette, Shield, User, X, type LucideIcon } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';

import { getAccountProfile } from '../../services/account.service';
import type { AccountProfile } from '../../types/account';

interface SidebarItemProps {
  icon: LucideIcon;
  label: string;
  subtitle: string;
  active: boolean;
  to: string;
  onNavigate?: () => void;
}

function SidebarItem({ icon: Icon, label, subtitle, active, to, onNavigate }: SidebarItemProps) {
  const navigate = useNavigate();
  return (
    <button
      type="button"
      onClick={() => {
        onNavigate?.();
        navigate(to);
      }}
      className={`flex w-full items-start gap-3 rounded-2xl border px-4 py-3 text-left transition ${
        active
          ? 'border-violet-300/35 bg-violet-600 text-white shadow-[0_18px_42px_rgba(124,58,237,0.26)]'
          : 'border-transparent text-slate-300 hover:border-white/10 hover:bg-white/[0.05] hover:text-white'
      }`}
      aria-current={active ? 'page' : undefined}
    >
      <Icon size={20} className="mt-0.5 shrink-0" />
      <span className="min-w-0">
        <span className="block text-base font-semibold">{label}</span>
        <span className={`mt-0.5 block text-sm ${active ? 'text-violet-100' : 'text-slate-500'}`}>{subtitle}</span>
      </span>
    </button>
  );
}

const links = [
  { to: '/app/account/overview', label: 'Perfil', subtitle: 'Suas informacoes pessoais', icon: User },
  { to: '/app/account/security', label: 'Seguranca', subtitle: 'Senha e autenticacao', icon: Shield },
  { to: '/app/account/preferences', label: 'Preferencias', subtitle: 'Idioma, tema e visual', icon: Palette },
  { to: '/app/account/notifications', label: 'Notificacoes', subtitle: 'Preferencias de alertas', icon: Bell },
  { to: '/app/account/sessions', label: 'Sessoes', subtitle: 'Dispositivos conectados', icon: Archive },
  { to: '/app/account/privacy', label: 'Privacidade', subtitle: 'Dados e permissoes', icon: Database },
];

export function AccountShell() {
  const location = useLocation();
  const [profile, setProfile] = useState<AccountProfile | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    void getAccountProfile().then(setProfile).catch(() => setProfile(null));
  }, []);

  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  const sidebar = (
    <div className="space-y-2">
      {links.map((item) => (
        <SidebarItem
          key={item.to}
          {...item}
          active={location.pathname === item.to || (item.to === '/app/account/overview' && location.pathname === '/app/account/profile')}
          onNavigate={() => setMobileMenuOpen(false)}
        />
      ))}
    </div>
  );

  return (
    <div className="space-y-6 pb-8 text-white">
      <header className="flex flex-col gap-2">
        <h1 className="font-display text-4xl">Minha conta</h1>
        <p className="text-sm text-slate-400">
          Gerencie suas informacoes pessoais, seguranca e preferencias.
          {profile?.name ? ` Conta de ${profile.name}.` : ''}
        </p>
      </header>

      <div className="lg:hidden">
        <button
          type="button"
          onClick={() => setMobileMenuOpen(true)}
          className="inline-flex items-center gap-2 rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm font-medium text-white"
        >
          <Menu size={18} />
          Abrir secoes da conta
        </button>
      </div>

      <div className="flex flex-col gap-6 lg:flex-row lg:items-start">
        <aside className="hidden w-full shrink-0 rounded-3xl border border-white/10 bg-gradient-to-b from-white/[0.04] to-transparent p-3 lg:sticky lg:top-6 lg:block lg:w-[320px] lg:max-h-[calc(100vh-8rem)] lg:overflow-auto">
          {sidebar}
        </aside>
        <main className="min-w-0 flex-1 space-y-4">
          <Outlet />
        </main>
      </div>

      {mobileMenuOpen ? (
        <div className="fixed inset-0 z-50 bg-ink/80 p-4 backdrop-blur-sm lg:hidden">
          <div className="h-full overflow-hidden rounded-3xl border border-white/10 bg-slate-950">
            <div className="flex items-center justify-between border-b border-white/10 px-4 py-4">
              <div>
                <p className="text-xs uppercase tracking-[0.24em] text-violet-300">Minha conta</p>
                <p className="mt-1 text-sm text-slate-300">Escolha a secao.</p>
              </div>
              <button
                type="button"
                onClick={() => setMobileMenuOpen(false)}
                className="grid h-10 w-10 place-items-center rounded-2xl border border-white/10 text-white"
                aria-label="Fechar menu da conta"
              >
                <X size={18} />
              </button>
            </div>
            <div className="h-[calc(100%-73px)] overflow-auto p-4">{sidebar}</div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
