import { useEffect, useState } from 'react';

import { getAccountPreferences, updateAccountPreferences } from '../../../services/settingsAccount.service';
import { useToast } from '../../../hooks/useToast';
import type { AccountPreferences } from '../../../types/account';
import { PreferencesForm } from '../PreferencesForm';

export function AccountPersonalizationPage() {
  const toast = useToast();
  const [prefs, setPrefs] = useState<AccountPreferences | null>(null);
  const [saving, setSaving] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [saveMessage, setSaveMessage] = useState('');

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
        setSaveStatus('idle');
        setSaveMessage('');
        try {
          setPrefs(await updateAccountPreferences(prefs));
          setSaveStatus('success');
          setSaveMessage('Alterações salvas com sucesso.');
          toast.success('Preferências atualizadas com sucesso.');
        } catch {
          setSaveStatus('error');
          setSaveMessage('Não foi possível salvar agora. Tente novamente em instantes.');
          toast.error('Erro ao salvar preferências da conta.');
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
