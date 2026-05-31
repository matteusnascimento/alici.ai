import { AnimatePresence, motion } from 'framer-motion';
import {
  Archive,
  Bell,
  CircleHelp,
  Database,
  Home,
  Languages,
  Menu,
  Palette,
  Puzzle,
  Scale,
  Shield,
  User,
  X,
  type LucideIcon,
} from 'lucide-react';
import { useEffect, useState } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';

import { getAccountProfile } from '../../services/account.service';
import type { AccountProfile } from '../../types/account';
import { AccountHeader } from './AccountHeader';

interface SidebarItemProps {
  icon: LucideIcon;
  label: string;
  subtitle: string;
  active: boolean;
  to: string;
  onNavigate?: () => void;
  emphasis?: 'default' | 'mobile';
}

function SidebarItem({ icon: Icon, label, subtitle, active, to, onNavigate, emphasis = 'default' }: SidebarItemProps) {
  const navigate = useNavigate();
  const isMobile = emphasis === 'mobile';

  return (
    <button
      type="button"
      onClick={() => {
        onNavigate?.();
        navigate(to);
      }}
      className={`w-full flex items-start gap-3 px-2.5 py-3 rounded-2xl border transition text-left ${
        active
          ? isMobile
            ? 'border-cyan-300/35 bg-cyan-300/12 text-white shadow-[0_12px_30px_rgba(34,211,238,0.12)]'
            : 'border-white/20 bg-white/10 text-white shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]'
          : 'border-transparent text-white/70 hover:border-white/10 hover:bg-white/5 hover:text-white/90'
      }`}
      aria-current={active ? 'page' : undefined}
    >
      <div className="w-5 h-5 shrink-0 mt-0.5 ml-0 flex items-center justify-center">
        <Icon size={18} />
      </div>

      <div className="min-w-0 flex-1">
        <p className="text-sm font-semibold leading-5">{label}</p>
        <p className={`text-xs leading-4 ${active ? (isMobile ? 'text-cyan-50/80' : 'text-white/70') : 'text-white/50'}`}>{subtitle}</p>
      </div>
    </button>
  );
}

const sections = [
  {
    title: 'Conta AXI',
    links: [
      { to: '/app/account/overview', label: 'Visão geral', subtitle: 'Resumo da conta e do plano', icon: Home },
      { to: '/app/account/profile', label: 'Perfil', subtitle: 'Dados pessoais e identidade', icon: User },
      { to: '/app/account/personalization', label: 'Preferências', subtitle: 'Tema, idioma e experiência', icon: Palette },
      { to: '/app/account/security', label: 'Segurança', subtitle: 'Senha e proteção da conta', icon: Shield },
      { to: '/app/account/applications', label: 'Integrações', subtitle: 'Apps e conexões ativas', icon: Puzzle },
    ],
  },
  {
    title: 'Suporte e dados',
    links: [
      { to: '/app/account/notifications', label: 'Notificações', subtitle: 'Alertas e comunicações', icon: Bell },
      { to: '/app/account/data-controls', label: 'Privacidade', subtitle: 'Exportação e exclusão de dados', icon: Database },
      { to: '/app/account/help', label: 'Ajuda', subtitle: 'Suporte e central de ajuda', icon: CircleHelp },
      { to: '/app/account/legal', label: 'Legal', subtitle: 'Termos e privacidade', icon: Scale },
    ],
  },
];

export function AccountShell() {
  const location = useLocation();
  const [profile, setProfile] = useState<AccountProfile | null>(null);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    void getAccountProfile()
      .then((profileData) => {
        setProfile(profileData);
      })
      .catch(() => {
        setProfile(null);
      });
  }, []);

  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  const sidebarContent = (
    <div className="space-y-5">
      {sections.map((section) => (
        <div key={section.title} className="space-y-2">
          <p className="px-1 text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-400">{section.title}</p>
          <div className="space-y-1.5">
            {section.links.map((item) => (
              <SidebarItem
                key={item.to}
                to={item.to}
                icon={item.icon}
                label={item.label}
                subtitle={item.subtitle}
                active={location.pathname === item.to || location.pathname.startsWith(`${item.to}/`)}
                onNavigate={() => setMobileMenuOpen(false)}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="space-y-6 pb-8">
      <AccountHeader
        title="Conta AXI"
        subtitle="Gerencie seu perfil pessoal, preferencias, seguranca da conta e dados individuais."
        profile={profile}
      />
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
        <aside className="hidden w-full shrink-0 rounded-3xl border border-white/10 bg-gradient-to-b from-white/[0.03] to-transparent p-3 lg:block lg:w-[320px] lg:sticky lg:top-6 lg:max-h-[calc(100vh-8rem)] lg:overflow-auto">
          {sidebarContent}
        </aside>
        <main className="min-w-0 flex-1 space-y-4">
          <Outlet />
        </main>
      </div>

      <AnimatePresence>
        {mobileMenuOpen ? (
          <motion.div
            className="fixed inset-0 z-40 bg-ink/70 backdrop-blur-sm lg:hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="absolute inset-x-4 top-4 bottom-4 overflow-hidden rounded-3xl border border-white/10 bg-[linear-gradient(180deg,rgba(7,14,32,0.98),rgba(9,20,38,0.96))] shadow-2xl"
              initial={{ opacity: 0, y: 18, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 16, scale: 0.98 }}
              transition={{ duration: 0.2, ease: 'easeOut' }}
            >
              <div className="flex items-center justify-between border-b border-white/10 px-4 py-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.24em] text-cyan-300">Conta AXI</p>
                  <p className="mt-1 text-sm text-slate-300">Escolha a secao que deseja abrir.</p>
                </div>
                <button
                  type="button"
                  onClick={() => setMobileMenuOpen(false)}
                  className="inline-flex h-10 w-10 items-center justify-center rounded-2xl border border-white/10 text-white"
                  aria-label="Fechar menu da conta"
                >
                  <X size={18} />
                </button>
              </div>
              <div className="h-[calc(100%-81px)] overflow-auto p-4">
                <div className="space-y-5">
                  {sections.map((section) => (
                    <div key={`mobile-${section.title}`} className="space-y-2">
                      <p className="px-1 text-[11px] font-semibold uppercase tracking-[0.2em] text-slate-400">{section.title}</p>
                      <div className="space-y-1.5">
                        {section.links.map((item) => (
                          <SidebarItem
                            key={`mobile-${item.to}`}
                            to={item.to}
                            icon={item.icon}
                            label={item.label}
                            subtitle={item.subtitle}
                            active={location.pathname === item.to || location.pathname.startsWith(`${item.to}/`)}
                            onNavigate={() => setMobileMenuOpen(false)}
                            emphasis="mobile"
                          />
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </div>
  );
}
