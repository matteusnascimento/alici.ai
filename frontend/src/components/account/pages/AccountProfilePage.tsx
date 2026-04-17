import { Check, Loader2, Upload, X } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

import { getAccountProfile, updateAccountProfile } from '../../../services/account.service';
import { useBilling } from '../../../hooks/useBilling';
import { useToast } from '../../../hooks/useToast';
import type { AccountProfileUpdate } from '../../../types/account';

// ── Profile header com avatar grande + identidade do usuário
function ProfileHeader({
  avatarUrl,
  name,
  planName,
  onAvatarChange,
}: {
  avatarUrl: string | null;
  name: string;
  planName: string;
  onAvatarChange: (url: string | null) => void;
}) {
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/account/upload-avatar', {
        method: 'POST',
        headers: { Authorization: `Bearer ${localStorage.getItem('axi_token')}` },
        body: formData,
      });

      if (!response.ok) throw new Error('Falha no upload');
      const data = (await response.json()) as { avatar_url: string };
      onAvatarChange(data.avatar_url);
    } catch (err) {
      console.error('Avatar upload error:', err);
    } finally {
      setUploading(false);
    }
  }

  const initials = name
    .split(' ')
    .slice(0, 2)
    .map((n) => n[0])
    .join('')
    .toUpperCase();

  return (
    <section className="rounded-3xl border border-white/10 bg-gradient-to-br from-white/[0.08] to-transparent p-6">
      <div className="flex items-start gap-6">
        {/* Avatar grande */}
        <div className="relative shrink-0">
          {avatarUrl ? (
            <img
              src={avatarUrl}
              alt={name}
              className="h-28 w-28 rounded-3xl border-2 border-white/10 object-cover"
            />
          ) : (
            <div className="flex h-28 w-28 items-center justify-center rounded-3xl border-2 border-white/10 bg-gradient-to-br from-cyan/20 to-blue/20">
              <span className="text-3xl font-bold text-cyan">{initials}</span>
            </div>
          )}

          {/* Botão upload overlay */}
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="absolute bottom-1 right-1 flex items-center justify-center rounded-full border border-white/20 bg-black/60 p-2 transition hover:border-cyan/40 hover:bg-black/80 disabled:opacity-50"
          >
            {uploading ? <Loader2 size={14} className="animate-spin" /> : <Upload size={14} />}
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={(e) => void handleFileUpload(e)}
            className="hidden"
          />
        </div>

        {/* Informações */}
        <div className="flex-1">
          <h1 className="font-display text-3xl text-white">{name}</h1>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <span className="rounded-full border border-cyan/40 bg-cyan/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.1em] text-cyan">
              Plano {planName}
            </span>
            <span className="rounded-full border border-emerald-400/40 bg-emerald-500/15 px-3 py-1 text-xs font-semibold uppercase tracking-[0.1em] text-emerald-300">
              Ativo
            </span>
          </div>
          <p className="mt-3 text-sm text-slate-400">
            Sua foto e nome são exibidos em agentes, contatos e configurações publicamente.
          </p>
        </div>
      </div>
    </section>
  );
}

// ── Form section com título
function FormSection({
  title,
  description,
  children,
}: {
  title: string;
  description?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
      <div className="mb-5">
        <h3 className="font-display text-lg text-white">{title}</h3>
        {description && <p className="mt-1 text-xs text-slate-400">{description}</p>}
      </div>
      {children}
    </section>
  );
}

// ── Input component
function FormInput({
  label,
  type = 'text',
  value,
  onChange,
  placeholder,
  disabled = false,
}: {
  label: string;
  type?: string;
  value: string | null;
  onChange: (v: string | null) => void;
  placeholder?: string;
  disabled?: boolean;
}) {
  return (
    <label className="block space-y-1.5 text-sm">
      <span className="font-medium text-slate-300">{label}</span>
      <input
        type={type}
        value={value ?? ''}
        onChange={(e) => onChange(e.target.value || null)}
        placeholder={placeholder}
        disabled={disabled}
        className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white placeholder:text-slate-500 transition focus:border-cyan/50 focus:outline-none focus:ring-2 focus:ring-cyan/20 disabled:opacity-60"
      />
    </label>
  );
}

// ── Textarea component
function FormTextarea({
  label,
  value,
  onChange,
  placeholder,
  maxLength,
}: {
  label: string;
  value: string | null;
  onChange: (v: string | null) => void;
  placeholder?: string;
  maxLength?: number;
}) {
  const current = value ?? '';
  return (
    <label className="block space-y-1.5 text-sm">
      <div className="flex items-center justify-between">
        <span className="font-medium text-slate-300">{label}</span>
        {maxLength && (
          <span className={`text-xs ${current.length >= maxLength * 0.9 ? 'text-amber-400' : 'text-slate-500'}`}>
            {current.length} / {maxLength}
          </span>
        )}
      </div>
      <textarea
        value={current}
        onChange={(e) => onChange(e.target.value || null)}
        placeholder={placeholder}
        maxLength={maxLength}
        className="h-24 w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white placeholder:text-slate-500 transition focus:border-cyan/50 focus:outline-none focus:ring-2 focus:ring-cyan/20"
      />
    </label>
  );
}

export function AccountProfilePage() {
  const { pushToast } = useToast();
  const { current } = useBilling();
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

  return (
    <div className="space-y-5">
      {/* Header com avatar + identidade */}
      <ProfileHeader
        avatarUrl={form.avatar_url ?? null}
        name={form.name}
        planName={current?.plan_name ?? 'Free'}
        onAvatarChange={(url) => setForm((cur) => (cur ? { ...cur, avatar_url: url } : cur))}
      />

      {/* Dados principais */}
      <FormSection title="Dados principais" description="Nome, email e telefone de contato">
        <div className="grid gap-4 md:grid-cols-2">
          <FormInput
            label="Nome completo"
            value={form.name}
            onChange={(v) => setForm((cur) => (cur ? { ...cur, name: v ?? '' } : cur))}
            placeholder="Seu nome completo"
          />
          <FormInput
            label="Email"
            type="email"
            value={form.email}
            onChange={(v) => setForm((cur) => (cur ? { ...cur, email: v ?? '' } : cur))}
            placeholder="seu@email.com"
          />
          <FormInput
            label="Telefone"
            type="tel"
            value={form.phone}
            onChange={(v) => setForm((cur) => (cur ? { ...cur, phone: v } : cur))}
            placeholder="(11) 99999-9999"
          />
        </div>
      </FormSection>

      {/* Conta */}
      <FormSection title="Conta" description="Username e bio pública">
        <div className="grid gap-4 md:grid-cols-2">
          <FormInput
            label="Username"
            value={form.username}
            onChange={(v) => setForm((cur) => (cur ? { ...cur, username: v ?? '' } : cur))}
            placeholder="seu-username"
          />
        </div>
        <div className="mt-4">
          <FormTextarea
            label="Bio"
            value={form.bio}
            onChange={(v) => setForm((cur) => (cur ? { ...cur, bio: v } : cur))}
            placeholder="Conte um pouco sobre você ou sua empresa…"
            maxLength={160}
          />
        </div>
      </FormSection>

      {/* Ações */}
      <div className="flex items-center justify-end gap-3 pt-2">
        <button
          type="button"
          onClick={() => {
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
          }}
          disabled={saving}
          className="rounded-2xl border border-white/20 px-5 py-2.5 text-sm font-semibold text-slate-300 transition hover:border-white/30 hover:text-white disabled:opacity-60"
        >
          Cancelar
        </button>
        <button
          type="button"
          onClick={save}
          disabled={saving}
          className={`inline-flex items-center gap-2 rounded-2xl px-5 py-2.5 text-sm font-semibold transition ${
            saved
              ? 'border border-emerald-400/40 bg-emerald-500/15 text-emerald-300'
              : 'bg-cyan text-ink hover:bg-cyan/90 disabled:opacity-60'
          }`}
        >
          {saving ? (
            <Loader2 size={15} className="animate-spin" />
          ) : saved ? (
            <Check size={15} />
          ) : null}
          {saving ? 'Salvando…' : saved ? 'Salvo!' : 'Salvar alterações'}
        </button>
      </div>
    </div>
  );
}
