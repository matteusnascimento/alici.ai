import type { AccountPreferences } from '../../types/account';

interface PreferencesFormProps {
  value: AccountPreferences;
  onChange: (next: AccountPreferences) => void;
  onSave: () => void;
  saving: boolean;
}

export function PreferencesForm({ value, onChange, onSave, saving }: PreferencesFormProps) {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
      <h2 className="font-display text-2xl text-white">Personalization</h2>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        {[
          ['language', 'Language'],
          ['voice', 'Voice'],
          ['theme_mode', 'Appearance'],
          ['accent_color', 'Accent color'],
        ].map(([key, label]) => (
          <label key={key} className="block space-y-2 text-sm text-slate-300">
            <span>{label}</span>
            <input
              value={value[key as keyof AccountPreferences] as string}
              onChange={(event) => onChange({ ...value, [key]: event.target.value })}
              className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white"
            />
          </label>
        ))}
      </div>
      <div className="mt-4 space-y-2">
        {[
          ['haptic_feedback', 'Haptic/feedback'],
          ['background_conversation', 'Background conversation'],
          ['autocomplete', 'Autocomplete'],
          ['trending', 'Trending'],
          ['sequence', 'Sequence'],
          ['split_mode', 'Split mode'],
        ].map(([key, label]) => (
          <label key={key} className="flex items-center justify-between rounded-2xl border border-white/10 bg-ink/40 px-4 py-3 text-sm text-slate-100">
            <span>{label}</span>
            <input
              type="checkbox"
              checked={Boolean(value[key as keyof AccountPreferences])}
              onChange={(event) => onChange({ ...value, [key]: event.target.checked })}
            />
          </label>
        ))}
      </div>
      <button type="button" onClick={onSave} disabled={saving} className="mt-4 rounded-2xl bg-sand px-4 py-2 text-sm font-semibold text-ink">
        {saving ? 'Salvando...' : 'Salvar preferencias'}
      </button>
    </section>
  );
}
