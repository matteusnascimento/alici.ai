import { useEffect, useState } from 'react';

import { getAccountPreferences, updateAccountPreferences } from '../../../services/settingsAccount.service';
import type { AccountPreferences } from '../../../types/account';

export function AccountLanguagePage() {
  const [prefs, setPrefs] = useState<AccountPreferences | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    void getAccountPreferences().then(setPrefs);
  }, []);

  if (!prefs) {
    return <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-5 text-slate-300">Carregando preferencias...</div>;
  }

  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
      <h2 className="font-display text-2xl text-white">Language / Appearance</h2>
      <div className="mt-4 grid gap-3 md:grid-cols-3">
        {[
          ['language', 'Language'],
          ['theme_mode', 'Theme mode'],
          ['accent_color', 'Accent color'],
        ].map(([key, label]) => (
          <label key={key} className="block space-y-2 text-sm text-slate-300">
            <span>{label}</span>
            <input
              value={prefs[key as keyof AccountPreferences] as string}
              onChange={(event) => setPrefs((current) => (current ? { ...current, [key]: event.target.value } : current))}
              className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white"
            />
          </label>
        ))}
      </div>
      <button
        type="button"
        onClick={async () => {
          setSaving(true);
          try {
            setPrefs(await updateAccountPreferences(prefs));
          } finally {
            setSaving(false);
          }
        }}
        className="mt-4 rounded-2xl bg-sand px-4 py-2 text-sm font-semibold text-ink"
      >
        {saving ? 'Salvando...' : 'Salvar'}
      </button>
    </section>
  );
}
