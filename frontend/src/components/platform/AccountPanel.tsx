import { FormEvent, useEffect, useState } from 'react';

import { useSettings } from '../../hooks/useSettings';

export function AccountPanel() {
  const { account, loading, saving, error, saveProfile, saveSettings } = useSettings();
  const [profile, setProfile] = useState({ name: '', username: '', email: '', phone: '', plan: 'starter' });
  const [settings, setLocalSettings] = useState({
    background_conversation: true,
    autocomplete: true,
    trending: true,
    sequence: false,
    split_mode: false,
    language: 'pt-BR',
    voice: 'neutral',
  });

  useEffect(() => {
    if (account) {
      setProfile({
        name: account.profile.name,
        username: account.profile.username,
        email: account.profile.email,
        phone: account.profile.phone || '',
        plan: account.profile.plan,
      });
      setLocalSettings(account.settings);
    }
  }, [account]);

  async function handleProfileSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await saveProfile(profile);
  }

  async function handleSettingsSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await saveSettings(settings);
  }

  if (loading) {
    return <div className="panel-base">Carregando conta...</div>;
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
      <section className="panel-base">
        <h3 className="font-display text-2xl text-white">Perfil</h3>
        <form className="mt-6 grid gap-4" onSubmit={handleProfileSubmit}>
          {[
            ['name', 'Nome'],
            ['username', 'Username'],
            ['email', 'Email'],
            ['phone', 'Telefone'],
            ['plan', 'Plano'],
          ].map(([key, label]) => (
            <div key={key}>
              <label className="mb-2 block text-sm text-slate-300">{label}</label>
              <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none focus:border-cyan" type={key === 'email' ? 'email' : 'text'} value={profile[key as keyof typeof profile]} onChange={(event) => setProfile((current) => ({ ...current, [key]: event.target.value }))} required={key !== 'phone'} />
            </div>
          ))}
          <button className="rounded-2xl bg-sand px-4 py-3 font-semibold text-ink transition hover:bg-white disabled:opacity-60" disabled={saving} type="submit">
            Salvar perfil
          </button>
        </form>
      </section>
      <section className="panel-base">
        <h3 className="font-display text-2xl text-white">Configurações AXI</h3>
        <form className="mt-6 space-y-4" onSubmit={handleSettingsSubmit}>
          {[
            ['background_conversation', 'Background conversation'],
            ['autocomplete', 'Autocomplete'],
            ['trending', 'Trending'],
            ['sequence', 'Sequence'],
            ['split_mode', 'Split mode'],
          ].map(([key, label]) => (
            <label key={key} className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white">
              <span>{label}</span>
              <input checked={settings[key as keyof typeof settings] as boolean} onChange={(event) => setLocalSettings((current) => ({ ...current, [key]: event.target.checked }))} type="checkbox" />
            </label>
          ))}
          {[
            ['language', 'Idioma'],
            ['voice', 'Voz'],
          ].map(([key, label]) => (
            <div key={key}>
              <label className="mb-2 block text-sm text-slate-300">{label}</label>
              <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none focus:border-cyan" value={settings[key as keyof typeof settings] as string} onChange={(event) => setLocalSettings((current) => ({ ...current, [key]: event.target.value }))} />
            </div>
          ))}
          <button className="rounded-2xl bg-sand px-4 py-3 font-semibold text-ink transition hover:bg-white disabled:opacity-60" disabled={saving} type="submit">
            Salvar configurações
          </button>
        </form>
        {error ? <p className="mt-4 text-sm text-coral">{error}</p> : null}
      </section>
    </div>
  );
}
