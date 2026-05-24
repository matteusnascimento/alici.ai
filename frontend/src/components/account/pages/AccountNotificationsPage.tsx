import { useEffect, useState } from 'react';

import { getAccountNotifications, updateAccountNotifications } from '../../../services/settingsAccount.service';
import type { AccountNotifications } from '../../../types/account';
import { NotificationSettingsForm } from '../NotificationSettingsForm';

export function AccountNotificationsPage() {
  const [notifications, setNotifications] = useState<AccountNotifications | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    void getAccountNotifications().then(setNotifications);
  }, []);

  if (!notifications) {
    return <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-5 text-slate-300">Carregando notificacoes...</div>;
  }

  return (
    <NotificationSettingsForm
      value={notifications}
      onChange={setNotifications}
      onSave={async () => {
        setSaving(true);
        try {
          setNotifications(await updateAccountNotifications(notifications));
        } finally {
          setSaving(false);
        }
      }}
      saving={saving}
    />
  );
}
