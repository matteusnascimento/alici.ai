import { Check, Globe2, Loader2, Moon, Save, Sun } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

import { getAccountPreferences, updateAccountPreferences } from '../../../services/settingsAccount.service';
import { useToast } from '../../../hooks/useToast';
import type { AccountPreferences } from '../../../types/account';

export function AccountLanguagePage() {
  const { pushToast } = useToast();
  const [prefs, setPrefs] = useState<AccountPreferences | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const savedTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    void getAccountPreferences().then(setPrefs);
  }, []);

  if (!prefs) {
    return (
      <div className="flex items-center gap-3 rounded-3xl border border-white/10 bg-white/[0.03] p-5 text-slate-300">
        <Loader2 size={16} className="animate-spin text-cyan-300" /> Carregando preferências…
      </div>
    );
  }

  async function handleSave() {
    if (!prefs) return;
    setSaving(true);
    setSaved(false);
    try {
      const updated = await updateAccountPreferences(prefs);
      setPrefs(updated);
      setSaved(true);
      pushToast('Preferências de idioma e aparência salvas.', 'success');
      if (savedTimer.current) clearTimeout(savedTimer.current);
      savedTimer.current = setTimeout(() => setSaved(false), 2500);
    } catch {
      pushToast('Erro ao salvar preferências.', 'error');
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
      <div className="mb-5 flex items-center gap-3">
        <Globe2 size={20} className="text-cyan-300" />
        <div>
          <h2 className="font-display text-2xl text-white">Idioma e Aparência</h2>
          <p className="mt-0.5 text-sm text-slate-400">Configure o idioma e o tema visual da plataforma.</p>
        </div>
      </div>

      <div className="grid gap-5 md:grid-cols-2">
        <label className="block space-y-1.5 text-sm">
          <span className="font-medium text-slate-300">Idioma</span>
          <select
            value={prefs.language}
            onChange={(e) => setPrefs((p) => p ? { ...p, language: e.target.value } : p)}
            className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white transition focus:border-cyan/50 focus:outline-none focus:ring-2 focus:ring-cyan/20"
          >
            <option value="pt-BR">Português (Brasil)</option>
            <option value="en-US">English (US)</option>
            <option value="es">Español</option>
            <option value="fr">Français</option>
          </select>
        </label>

        <div className="space-y-1.5">
          <span className="text-sm font-medium text-slate-300">Tema</span>
          <div className="flex gap-2">
            {(['dark', 'light'] as const).map((mode) => (
              <button
                key={mode}
                type="button"
                onClick={() => setPrefs((p) => p ? { ...p, theme_mode: mode } : p)}
                className={`flex flex-1 items-center justify-center gap-2 rounded-2xl border py-3 text-sm font-medium transition ${
                  prefs.theme_mode === mode
                    ? 'border-cyan/50 bg-cyan/10 text-cyan'
                    : 'border-white/10 bg-ink/40 text-slate-300 hover:border-white/20'
                }`}
              >
                {mode === 'dark' ? <Moon size={14} /> : <Sun size={14} />}
                {mode === 'dark' ? 'Escuro' : 'Claro'}
              </button>
            ))}
          </div>
        </div>
      </div>

      <button
        type="button"
        disabled={saving}
        onClick={() => void handleSave()}
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
