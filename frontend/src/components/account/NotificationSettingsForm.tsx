import { Bell, BellOff, Check, Loader2, Save, ShieldAlert, Sparkles, Tag } from 'lucide-react';
import { useRef, useState } from 'react';

import { useToast } from '../../hooks/useToast';
import type { AccountNotifications } from '../../types/account';

interface NotificationSettingsFormProps {
  value: AccountNotifications;
  onChange: (next: AccountNotifications) => void;
  onSave: () => void;
  saving: boolean;
}

interface NotifGroup {
  label: string;
  icon: React.ReactNode;
  rows: Array<[keyof AccountNotifications, string, string]>;
}

const GROUPS: NotifGroup[] = [
  {
    label: 'Geral',
    icon: <Bell size={14} className="text-cyan-300" />,
    rows: [
      ['notifications_enabled', 'Ativar notificações', 'Controle mestre de todas as notificações'],
      ['push_notifications', 'Notificações push', 'Alertas no navegador ou dispositivo móvel'],
      ['email_notifications', 'Notificações por email', 'Resumos e alertas importantes no seu email'],
    ],
  },
  {
    label: 'Produto',
    icon: <Sparkles size={14} className="text-purple-300" />,
    rows: [
      ['product_updates', 'Atualizações do produto', 'Novos recursos, melhorias e changelogs'],
    ],
  },
  {
    label: 'Marketing',
    icon: <Tag size={14} className="text-amber-300" />,
    rows: [
      ['marketing_notifications', 'Comunicações de marketing', 'Promoções, newsletters e conteúdo da AXI'],
    ],
  },
  {
    label: 'Segurança',
    icon: <ShieldAlert size={14} className="text-rose-300" />,
    rows: [
      ['security_alerts', 'Alertas de segurança', 'Acessos suspeitos, logins de novos dispositivos'],
    ],
  },
];

function Toggle({
  checked,
  onChange,
  disabled,
}: {
  checked: boolean;
  onChange: (v: boolean) => void;
  disabled?: boolean;
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      disabled={disabled}
      onClick={() => onChange(!checked)}
      className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 focus:outline-none disabled:opacity-40 ${
        checked ? 'bg-cyan' : 'bg-white/15'
      }`}
    >
      <span
        className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
          checked ? 'translate-x-4' : 'translate-x-0'
        }`}
      />
    </button>
  );
}

export function NotificationSettingsForm({ value, onChange, onSave, saving }: NotificationSettingsFormProps) {
  const { pushToast } = useToast();
  const [saved, setSaved] = useState(false);
  const savedTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  async function handleSave() {
    try {
      await Promise.resolve(onSave());
      setSaved(true);
      pushToast('Preferências de notificação salvas.', 'success');
      if (savedTimer.current) clearTimeout(savedTimer.current);
      savedTimer.current = setTimeout(() => setSaved(false), 2500);
    } catch {
      pushToast('Erro ao salvar preferências.', 'error');
    }
  }

  const masterOff = !value.notifications_enabled;

  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
      <div className="mb-5 flex items-center gap-3">
        {masterOff ? <BellOff size={20} className="text-slate-400" /> : <Bell size={20} className="text-cyan-300" />}
        <div>
          <h2 className="font-display text-2xl text-white">Preferencias de notificacoes</h2>
          <p className="mt-0.5 text-sm text-slate-400">Controle canais e categorias de preferencia da sua conta.</p>
        </div>
      </div>

      <div className="space-y-5">
        {GROUPS.map((group) => (
          <div key={group.label}>
            <div className="mb-2 flex items-center gap-1.5">
              {group.icon}
              <span className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">{group.label}</span>
            </div>
            <div className="space-y-1">
              {group.rows.map(([key, label, description]) => {
                const isDisabled = masterOff && key !== 'notifications_enabled';
                return (
                  <label
                    key={key}
                    className={`flex items-center justify-between rounded-2xl border border-white/10 bg-ink/40 px-4 py-3 transition hover:bg-ink/60 ${
                      isDisabled ? 'opacity-40' : ''
                    }`}
                  >
                    <div>
                      <p className="text-sm font-medium text-slate-100">{label}</p>
                      <p className="text-xs text-slate-500">{description}</p>
                    </div>
                    <Toggle
                      checked={Boolean(value[key])}
                      onChange={(v) => onChange({ ...value, [key]: v })}
                      disabled={isDisabled}
                    />
                  </label>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      <button
        type="button"
        onClick={() => void handleSave()}
        disabled={saving}
        className={`mt-6 inline-flex items-center gap-2 rounded-2xl px-5 py-2.5 text-sm font-semibold transition ${
          saved
            ? 'border border-emerald-400/40 bg-emerald-500/15 text-emerald-300'
            : 'bg-sand text-ink hover:bg-sand/90 disabled:opacity-60'
        }`}
      >
        {saving ? <Loader2 size={15} className="animate-spin" /> : saved ? <Check size={15} /> : <Save size={15} />}
        {saving ? 'Salvando…' : saved ? 'Salvo!' : 'Salvar preferências'}
      </button>
    </section>
  );
}
