import { useEffect, useState } from 'react';

import { getAccountProfile, updateAccountProfile } from '../../../services/account.service';
import type { AccountProfileUpdate } from '../../../types/account';
import { AvatarUploader } from '../AvatarUploader';

export function AccountProfilePage() {
  const [form, setForm] = useState<AccountProfileUpdate | null>(null);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void getAccountProfile().then((profile) => {
      setForm({
        name: profile.name,
        username: profile.username,
        email: profile.email,
        phone: profile.phone,
        avatar_url: profile.avatar_url,
        bio: profile.bio,
      });
    });
  }, []);

  if (!form) {
    return <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-5 text-slate-300">Carregando perfil...</div>;
  }

  async function save() {
    const payload = form;
    if (!payload) {
      return;
    }

    setSaving(true);
    setError(null);
    setMessage(null);
    try {
      await updateAccountProfile(payload);
      setMessage('Perfil atualizado com sucesso.');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao atualizar perfil');
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
      <h2 className="font-display text-2xl text-white">Profile Information</h2>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        {[
          ['name', 'Full name'],
          ['username', 'Username'],
          ['email', 'Email'],
          ['phone', 'Phone'],
        ].map(([key, label]) => (
          <label key={key} className="block space-y-2 text-sm text-slate-300">
            <span>{label}</span>
            <input
              type={key === 'email' ? 'email' : 'text'}
              value={(form[key as keyof AccountProfileUpdate] as string | null) || ''}
              onChange={(event) => setForm((current) => (current ? { ...current, [key]: event.target.value || null } : current))}
              className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white"
            />
          </label>
        ))}
      </div>
      <div className="mt-3 grid gap-3 md:grid-cols-2">
        <AvatarUploader value={form.avatar_url || ''} onChange={(next) => setForm((current) => (current ? { ...current, avatar_url: next || null } : current))} />
        <label className="block space-y-2 text-sm text-slate-300">
          <span>Bio</span>
          <textarea
            value={form.bio || ''}
            onChange={(event) => setForm((current) => (current ? { ...current, bio: event.target.value || null } : current))}
            className="h-28 w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white"
          />
        </label>
      </div>
      <div className="mt-4 flex gap-2">
        <button type="button" onClick={save} disabled={saving} className="rounded-2xl bg-sand px-4 py-2 text-sm font-semibold text-ink">
          {saving ? 'Salvando...' : 'Salvar perfil'}
        </button>
      </div>
      {message ? <p className="mt-3 text-sm text-cyan">{message}</p> : null}
      {error ? <p className="mt-3 text-sm text-coral">{error}</p> : null}
    </section>
  );
}
