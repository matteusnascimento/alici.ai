import { useEffect, useState } from 'react';

import { getAccountPreferences, updateAccountPreferences } from '../../../services/settingsAccount.service';
import type { AccountPreferences } from '../../../types/account';
import { PreferencesForm } from '../PreferencesForm';

export function AccountPersonalizationPage() {
  const [prefs, setPrefs] = useState<AccountPreferences | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    void getAccountPreferences().then(setPrefs);
  }, []);

  if (!prefs) {
    return <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-5 text-slate-300">Carregando preferencias...</div>;
  }

  return (
    <PreferencesForm
      value={prefs}
      onChange={setPrefs}
      onSave={async () => {
        setSaving(true);
        try {
          setPrefs(await updateAccountPreferences(prefs));
        } finally {
          setSaving(false);
        }
      }}
      saving={saving}
    />
  );
}
