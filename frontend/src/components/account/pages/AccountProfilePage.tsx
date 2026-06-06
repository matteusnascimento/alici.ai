import { Check, Loader2, Mail, Phone, Upload } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';

import {
  confirmEmailVerification,
  confirmPhoneVerification,
  getAccountProfile,
  requestEmailVerification,
  requestPhoneVerification,
  updateAccountProfile,
  uploadAccountAvatar,
} from '../../../services/account.service';
import { useToast } from '../../../hooks/useToast';
import type { AccountProfile, AccountProfileUpdate, AccountVerificationChallenge } from '../../../types/account';

function FormSection({ title, description, children }: { title: string; description: string; children: React.ReactNode }) {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
      <div className="mb-5">
        <h2 className="font-display text-xl text-white">{title}</h2>
        <p className="mt-1 text-sm text-slate-400">{description}</p>
      </div>
      {children}
    </section>
  );
}

function FormInput({
  label,
  value,
  onChange,
  type = 'text',
  placeholder,
}: {
  label: string;
  value: string | null;
  onChange: (value: string | null) => void;
  type?: string;
  placeholder?: string;
}) {
  return (
    <label className="block text-sm text-slate-300">
      {label}
      <input
        type={type}
        value={value ?? ''}
        onChange={(event) => onChange(event.target.value || null)}
        placeholder={placeholder}
        className="mt-1 w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-cyan/50 focus:ring-2 focus:ring-cyan/20"
      />
    </label>
  );
}

function VerificationCard({
  icon: Icon,
  title,
  destination,
  verified,
  challenge,
  code,
  loading,
  confirming,
  onCodeChange,
  onRequest,
  onConfirm,
}: {
  icon: typeof Mail;
  title: string;
  destination: string | null;
  verified: boolean;
  challenge: AccountVerificationChallenge | null;
  code: string;
  loading: boolean;
  confirming: boolean;
  onCodeChange: (value: string) => void;
  onRequest: () => Promise<void>;
  onConfirm: () => Promise<void>;
}) {
  return (
    <article className="rounded-2xl border border-white/10 bg-white/[0.035] p-4">
      <div className="flex items-start gap-3">
        <span className="grid h-10 w-10 shrink-0 place-items-center rounded-2xl bg-cyan/10 text-cyan">
          <Icon size={18} />
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className="font-semibold text-white">{title}</p>
            <span className={`rounded-full px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] ${verified ? 'border border-emerald-400/30 bg-emerald-500/15 text-emerald-300' : 'border border-amber-400/30 bg-amber-500/15 text-amber-300'}`}>
              {verified ? 'Verificado' : 'Pendente'}
            </span>
          </div>
          <p className="mt-1 text-sm text-slate-400">{destination || 'Nao informado'}</p>
        </div>
      </div>

      {verified ? (
        <p className="mt-4 text-sm text-emerald-300">Confirmado com sucesso.</p>
      ) : (
        <div className="mt-4 space-y-3">
          {challenge ? (
            <div className="rounded-xl border border-cyan/20 bg-cyan/5 px-3 py-2 text-xs text-slate-200">
              <p>Codigo enviado para {challenge.destination}.</p>
              <p>Expira em {new Date(challenge.expires_at).toLocaleTimeString('pt-BR')}.</p>
              {challenge.preview_code ? <p className="mt-1 text-cyan">Previa dev: {challenge.preview_code}</p> : null}
            </div>
          ) : null}
          {challenge ? (
            <div className="flex flex-col gap-2 sm:flex-row">
              <input
                value={code}
                onChange={(event) => onCodeChange(event.target.value)}
                placeholder="Digite o codigo recebido"
                className="w-full rounded-xl border border-white/10 bg-ink/70 px-4 py-2.5 text-sm text-white outline-none placeholder:text-slate-500 focus:border-cyan/50"
              />
              <button type="button" onClick={() => void onConfirm()} disabled={confirming || code.trim().length < 4} className="rounded-xl bg-cyan px-4 py-2.5 text-sm font-semibold text-ink disabled:opacity-50">
                {confirming ? 'Confirmando...' : 'Confirmar'}
              </button>
            </div>
          ) : null}
          <button type="button" onClick={() => void onRequest()} disabled={loading} className="rounded-xl border border-white/15 px-4 py-2 text-sm font-semibold text-slate-100 hover:border-cyan/40 disabled:opacity-50">
            {loading ? 'Gerando codigo...' : 'Enviar codigo'}
          </button>
        </div>
      )}
    </article>
  );
}

export function AccountProfilePage() {
  const { pushToast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [profile, setProfile] = useState<AccountProfile | null>(null);
  const [form, setForm] = useState<AccountProfileUpdate | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [emailChallenge, setEmailChallenge] = useState<AccountVerificationChallenge | null>(null);
  const [phoneChallenge, setPhoneChallenge] = useState<AccountVerificationChallenge | null>(null);
  const [emailCode, setEmailCode] = useState('');
  const [phoneCode, setPhoneCode] = useState('');
  const [requestingEmail, setRequestingEmail] = useState(false);
  const [requestingPhone, setRequestingPhone] = useState(false);
  const [confirmingEmail, setConfirmingEmail] = useState(false);
  const [confirmingPhone, setConfirmingPhone] = useState(false);

  async function loadProfile() {
    const profileData = await getAccountProfile();
    setProfile(profileData);
    setForm({
      name: profileData.name,
      username: profileData.username,
      email: profileData.email,
      phone: profileData.phone,
      avatar_url: profileData.avatar_url,
      bio: profileData.bio,
      company: profileData.company,
      job_title: profileData.job_title,
      timezone: profileData.timezone,
      language: profileData.language,
    });
    setEmailChallenge(null);
    setPhoneChallenge(null);
    setEmailCode('');
    setPhoneCode('');
  }

  useEffect(() => {
    void loadProfile().catch((err) => pushToast(err instanceof Error ? err.message : 'Falha ao carregar perfil', 'error'));
  }, [pushToast]);

  async function handleAvatarUpload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      const data = await uploadAccountAvatar(file);
      setForm((current) => (current ? { ...current, avatar_url: data.avatar_url } : current));
      pushToast('Foto atualizada.', 'success');
    } catch (err) {
      pushToast(err instanceof Error ? err.message : 'Erro ao enviar foto', 'error');
    } finally {
      setUploading(false);
    }
  }

  async function save() {
    if (!form) return;
    setSaving(true);
    setSaved(false);
    try {
      const updated = await updateAccountProfile(form);
      setProfile(updated);
      setForm({
        name: updated.name,
        username: updated.username,
        email: updated.email,
        phone: updated.phone,
        avatar_url: updated.avatar_url,
        bio: updated.bio,
        company: updated.company,
        job_title: updated.job_title,
        timezone: updated.timezone,
        language: updated.language,
      });
      setSaved(true);
      pushToast('Perfil atualizado com sucesso.', 'success');
      window.setTimeout(() => setSaved(false), 2400);
    } catch (err) {
      pushToast(err instanceof Error ? err.message : 'Erro ao atualizar perfil', 'error');
    } finally {
      setSaving(false);
    }
  }

  async function requestEmail() {
    setRequestingEmail(true);
    try {
      const challenge = await requestEmailVerification();
      setEmailChallenge(challenge);
      pushToast(challenge.message, 'success');
    } catch (err) {
      pushToast(err instanceof Error ? err.message : 'Erro ao solicitar verificacao de email', 'error');
    } finally {
      setRequestingEmail(false);
    }
  }

  async function requestPhone() {
    setRequestingPhone(true);
    try {
      const challenge = await requestPhoneVerification();
      setPhoneChallenge(challenge);
      pushToast(challenge.message, 'success');
    } catch (err) {
      pushToast(err instanceof Error ? err.message : 'Erro ao solicitar verificacao de telefone', 'error');
    } finally {
      setRequestingPhone(false);
    }
  }

  async function confirmEmail() {
    setConfirmingEmail(true);
    try {
      const response = await confirmEmailVerification({ code: emailCode.trim() });
      pushToast(response.message, 'success');
      await loadProfile();
    } catch (err) {
      pushToast(err instanceof Error ? err.message : 'Erro ao confirmar email', 'error');
    } finally {
      setConfirmingEmail(false);
    }
  }

  async function confirmPhone() {
    setConfirmingPhone(true);
    try {
      const response = await confirmPhoneVerification({ code: phoneCode.trim() });
      pushToast(response.message, 'success');
      await loadProfile();
    } catch (err) {
      pushToast(err instanceof Error ? err.message : 'Erro ao confirmar telefone', 'error');
    } finally {
      setConfirmingPhone(false);
    }
  }

  if (!form || !profile) {
    return (
      <div className="flex items-center gap-3 rounded-3xl border border-white/10 bg-white/[0.03] p-5 text-slate-300">
        <Loader2 size={16} className="animate-spin text-cyan-300" /> Carregando perfil...
      </div>
    );
  }

  const initials = form.name
    .split(' ')
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase();

  return (
    <div className="space-y-5">
      <section className="rounded-3xl border border-white/10 bg-gradient-to-br from-white/[0.08] to-transparent p-6">
        <div className="flex flex-col gap-5 md:flex-row md:items-center">
          <div className="relative shrink-0">
            {form.avatar_url ? (
              <img src={form.avatar_url} alt={form.name} className="h-24 w-24 rounded-3xl border border-white/10 object-cover" />
            ) : (
              <div className="grid h-24 w-24 place-items-center rounded-3xl border border-white/10 bg-gradient-to-br from-cyan/20 to-blue/20 text-2xl font-bold text-cyan">
                {initials}
              </div>
            )}
            <button type="button" onClick={() => fileInputRef.current?.click()} disabled={uploading} className="absolute bottom-1 right-1 grid h-9 w-9 place-items-center rounded-full border border-white/20 bg-black/60 text-white hover:bg-black/80 disabled:opacity-50" aria-label="Alterar foto">
              {uploading ? <Loader2 size={14} className="animate-spin" /> : <Upload size={14} />}
            </button>
            <input ref={fileInputRef} type="file" accept="image/*" onChange={(event) => void handleAvatarUpload(event)} className="hidden" />
          </div>
          <div>
            <h1 className="font-display text-3xl text-white">{form.name}</h1>
            <p className="mt-1 text-sm text-slate-400">@{form.username}</p>
          </div>
        </div>
      </section>

      <FormSection title="Informacoes pessoais" description="Atualize somente dados pessoais, contato e preferencias basicas da sua conta.">
        <div className="grid gap-4 md:grid-cols-2">
          <FormInput label="Nome completo" value={form.name} onChange={(value) => setForm((current) => (current ? { ...current, name: value ?? '' } : current))} />
          <FormInput label="Username" value={form.username} onChange={(value) => setForm((current) => (current ? { ...current, username: value ?? '' } : current))} />
          <FormInput label="Email" type="email" value={form.email} onChange={(value) => setForm((current) => (current ? { ...current, email: value ?? '' } : current))} />
          <FormInput label="Telefone" type="tel" value={form.phone} onChange={(value) => setForm((current) => (current ? { ...current, phone: value } : current))} />
          <FormInput label="Idioma" value={form.language} onChange={(value) => setForm((current) => (current ? { ...current, language: value } : current))} placeholder="pt-BR" />
          <FormInput label="Fuso horario" value={form.timezone} onChange={(value) => setForm((current) => (current ? { ...current, timezone: value } : current))} placeholder="America/Sao_Paulo" />
        </div>
      </FormSection>

      <FormSection title="Verificacoes" description="Confirme email e telefone com os fluxos reais de seguranca da conta.">
        <div className="grid gap-4 lg:grid-cols-2">
          <VerificationCard
            icon={Mail}
            title="Email"
            destination={form.email}
            verified={profile.email_verified}
            challenge={emailChallenge}
            code={emailCode}
            loading={requestingEmail}
            confirming={confirmingEmail}
            onCodeChange={setEmailCode}
            onRequest={requestEmail}
            onConfirm={confirmEmail}
          />
          <VerificationCard
            icon={Phone}
            title="Telefone"
            destination={form.phone}
            verified={profile.phone_verified}
            challenge={phoneChallenge}
            code={phoneCode}
            loading={requestingPhone}
            confirming={confirmingPhone}
            onCodeChange={setPhoneCode}
            onRequest={requestPhone}
            onConfirm={confirmPhone}
          />
        </div>
      </FormSection>

      <div className="flex justify-end gap-3">
        <button type="button" onClick={() => void loadProfile()} disabled={saving} className="rounded-2xl border border-white/20 px-5 py-2.5 text-sm font-semibold text-slate-300 hover:text-white disabled:opacity-60">
          Cancelar
        </button>
        <button type="button" onClick={() => void save()} disabled={saving} className={`inline-flex items-center gap-2 rounded-2xl px-5 py-2.5 text-sm font-semibold ${saved ? 'border border-emerald-400/40 bg-emerald-500/15 text-emerald-300' : 'bg-cyan text-ink hover:bg-cyan/90 disabled:opacity-60'}`}>
          {saving ? <Loader2 size={15} className="animate-spin" /> : saved ? <Check size={15} /> : null}
          {saving ? 'Salvando...' : saved ? 'Salvo!' : 'Salvar alteracoes'}
        </button>
      </div>
    </div>
  );
}
