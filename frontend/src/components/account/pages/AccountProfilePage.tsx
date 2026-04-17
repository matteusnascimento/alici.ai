import { Check, Loader2, Save } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

import { getAccountProfile, updateAccountProfile } from '../../../services/account.service';
import { useToast } from '../../../hooks/useToast';
import type { AccountProfileUpdate } from '../../../types/account';
import { AvatarUploader } from '../AvatarUploader';

export function AccountProfilePage() {
  const { pushToast } = useToast();
  const [form, setForm] = useState<AccountProfileUpdate | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const savedTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

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
    return (
      <div className="flex items-center gap-3 rounded-3xl border border-white/10 bg-white/[0.03] p-5 text-slate-300">
        <Loader2 size={16} className="animate-spin text-cyan-300" /> Carregando perfil...
      </div>
    );
  }

  async function save() {
    const payload = form;
    if (!payload) return;

    setSaving(true);
    setSaved(false);
    try {
      await updateAccountProfile(payload);
      setSaved(true);
      pushToast('Perfil atualizado com sucesso.', 'success');
      if (savedTimerRef.current) clearTimeout(savedTimerRef.current);
      savedTimerRef.current = setTimeout(() => setSaved(false), 2500);
    } catch (err) {
      pushToast(err instanceof Error ? err.message : 'Erro ao atualizar perfil', 'error');
    } finally {
      setSaving(false);
    }
  }

  const fields: Array<[keyof AccountProfileUpdate, string, string]> = [
    ['name', 'Nome completo', 'text'],
    ['username', 'Username', 'text'],
    ['email', 'Email', 'email'],
    ['phone', 'Telefone', 'tel'],
  ];

  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
      <div className="mb-5 flex items-center gap-3">
        <div>
          <h2 className="font-display text-2xl text-white">Informações do Perfil</h2>
          <p className="mt-0.5 text-sm text-slate-400">Seu nome e foto são exibidos para agentes e contatos.</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {fields.map(([key, label, type]) => (
          <label key={key} className="block space-y-1.5 text-sm">
            <span className="font-medium text-slate-300">{label}</span>
            <input
              type={type}
              value={(form[key as keyof AccountProfileUpdate] as string | null) ?? ''}
              onChange={(e) => setForm((cur) => (cur ? { ...cur, [key]: e.target.value || null } : cur))}
              className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white placeholder:text-slate-500 transition focus:border-cyan/50 focus:outline-none focus:ring-2 focus:ring-cyan/20"
            />
          </label>
        ))}
      </div>

      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <AvatarUploader
          value={form.avatar_url ?? ''}
          onChange={(next) => setForm((cur) => (cur ? { ...cur, avatar_url: next || null } : cur))}
        />
        <label className="block space-y-1.5 text-sm">
          <span className="font-medium text-slate-300">Bio</span>
          <textarea
            value={form.bio ?? ''}
            onChange={(e) => setForm((cur) => (cur ? { ...cur, bio: e.target.value || null } : cur))}
            placeholder="Conte um pouco sobre você ou sua empresa…"
            className="h-28 w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white placeholder:text-slate-500 transition focus:border-cyan/50 focus:outline-none focus:ring-2 focus:ring-cyan/20"
          />
        </label>
      </div>

      <div className="mt-5 flex items-center gap-3">
        <button
          type="button"
          onClick={save}
          disabled={saving}
          className={`inline-flex items-center gap-2 rounded-2xl px-5 py-2.5 text-sm font-semibold transition ${
            saved
              ? 'border border-emerald-400/40 bg-emerald-500/15 text-emerald-300'
              : 'bg-sand text-ink hover:bg-sand/90 disabled:opacity-60'
          }`}
        >
          {saving ? (
            <Loader2 size={15} className="animate-spin" />
          ) : saved ? (
            <Check size={15} />
          ) : (
            <Save size={15} />
          )}
          {saving ? 'Salvando…' : saved ? 'Salvo!' : 'Salvar perfil'}
        </button>
      </div>
    </section>
  );
}
