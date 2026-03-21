import { useEffect, useState } from 'react';

import { getAccountData, updateProfile, updateSettings } from '../services/settings.service';
import type { AccountData, Profile, UserSettings } from '../types/settings';

export function useSettings() {
  const [account, setAccount] = useState<AccountData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loadAccount() {
    setLoading(true);
    try {
      const data = await getAccountData();
      setAccount(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao carregar conta');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadAccount();
  }, []);

  async function saveProfile(payload: Profile) {
    setSaving(true);
    try {
      const profile = await updateProfile(payload);
      setAccount((current) => (current ? { ...current, profile } : current));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao salvar perfil');
      throw err;
    } finally {
      setSaving(false);
    }
  }

  async function saveSettings(payload: UserSettings) {
    setSaving(true);
    try {
      const settings = await updateSettings(payload);
      setAccount((current) => (current ? { ...current, settings } : current));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao salvar configurações');
      throw err;
    } finally {
      setSaving(false);
    }
  }

  return { account, loading, saving, error, saveProfile, saveSettings, reload: loadAccount };
}
