import { useEffect, useState } from 'react';

import { useToast } from '../../../hooks/useToast';
import { useTheme } from '../../../contexts/ThemeContext';
import type { AccountPreferences } from '../../../types/account';
import { PreferencesForm } from '../PreferencesForm';

export function AccountPersonalizationPage() {
  const toast = useToast();
  const { preferences, isLoading, savePreferences, applyTheme } = useTheme();
  const [prefs, setPrefs] = useState<AccountPreferences | null>(preferences);
  const [saving, setSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [saveMessage, setSaveMessage] = useState('');

  useEffect(() => {
    setPrefs(preferences);
  }, [preferences]);

  if (isLoading || !prefs) {
    return <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-5 text-slate-300">Carregando preferencias...</div>;
  }

  const handleChange = (next: AccountPreferences) => {
    setPrefs(next);
    applyTheme(next);
    setSaveStatus('idle');
    setSaveMessage('');
  };

  return (
    <PreferencesForm
      value={prefs}
      onChange={handleChange}
      onSave={async () => {
        setSaving(true);
        setSaveStatus('idle');
        setSaveMessage('');
        try {
          const updated = await savePreferences(prefs);
          setPrefs(updated);
          setSaveStatus('success');
          setSaveMessage('Alteracoes salvas com sucesso.');
          toast.success('Preferencias atualizadas com sucesso.');
        } catch {
          setSaveStatus('error');
          setSaveMessage('Nao foi possivel salvar agora. Tente novamente em instantes.');
          toast.error('Erro ao salvar preferencias da conta.');
        } finally {
          setSaving(false);
        }
      }}
      saving={saving}
      saveStatus={saveStatus}
      saveMessage={saveMessage}
    />
  );
}
