import type { AccountNotifications } from '../../types/account';

interface NotificationSettingsFormProps {
  value: AccountNotifications;
  onChange: (next: AccountNotifications) => void;
  onSave: () => void;
  saving: boolean;
}

export function NotificationSettingsForm({ value, onChange, onSave, saving }: NotificationSettingsFormProps) {
  const rows: Array<[keyof AccountNotifications, string]> = [
    ['notifications_enabled', 'Ativar notificacoes'],
    ['email_notifications', 'Notificacoes por email'],
    ['push_notifications', 'Notificacoes push'],
    ['product_updates', 'Atualizacoes do produto'],
    ['marketing_notifications', 'Comunicacoes de marketing'],
    ['security_alerts', 'Alertas de seguranca'],
  ];

  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
      <h2 className="font-display text-2xl text-white">Notifications</h2>
      <div className="mt-4 space-y-2">
        {rows.map(([key, label]) => (
          <label key={key} className="flex items-center justify-between rounded-2xl border border-white/10 bg-ink/40 px-4 py-3 text-sm text-slate-100">
            <span>{label}</span>
            <input
              type="checkbox"
              checked={Boolean(value[key])}
              onChange={(event) => onChange({ ...value, [key]: event.target.checked })}
            />
          </label>
        ))}
      </div>
      <button type="button" onClick={onSave} disabled={saving} className="mt-4 rounded-2xl bg-sand px-4 py-2 text-sm font-semibold text-ink">
        {saving ? 'Salvando...' : 'Salvar notificacoes'}
      </button>
    </section>
  );
}
