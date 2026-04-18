import { AlertCircle, BriefcaseBusiness, Check, Clock3, Loader2, Mail, ShieldCheck, Smartphone, Upload, UserCircle2 } from 'lucide-react';
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
import { useBilling } from '../../../hooks/useBilling';
import { useToast } from '../../../hooks/useToast';
import type { AccountProfile, AccountVerificationChallenge } from '../../../types/account';
import type { AccountProfileUpdate } from '../../../types/account';

// ── Profile header com avatar grande + identidade do usuário
function ProfileHeader({
  avatarUrl,
  name,
  username,
  planName,
  status,
  onAvatarChange,
}: {
  avatarUrl: string | null;
  name: string;
  username: string;
  planName: string;
  status: string;
  onAvatarChange: (url: string | null) => void;
}) {
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function handleFileUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const data = await uploadAccountAvatar(file);
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
          <p className="mt-1 text-sm text-slate-400">@{username}</p>
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <span className="rounded-full border border-cyan/40 bg-cyan/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.1em] text-cyan">
              Plano {planName}
            </span>
            <span className="rounded-full border border-emerald-400/40 bg-emerald-500/15 px-3 py-1 text-xs font-semibold uppercase tracking-[0.1em] text-emerald-300">
              {status}
            </span>
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className="rounded-full border border-white/15 px-3 py-1 text-xs font-semibold uppercase tracking-[0.1em] text-slate-200 transition hover:border-cyan/40 hover:text-white disabled:opacity-50"
            >
              Alterar foto
            </button>
          </div>
          <p className="mt-3 text-sm text-slate-400">
            Sua identidade é usada em agentes, integrações, histórico operacional e configurações da plataforma.
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

function StatusItem({ icon: Icon, label, value, tone = 'default' }: { icon: typeof Mail; label: string; value: string; tone?: 'default' | 'success' | 'warning' }) {
  const toneClass =
    tone === 'success'
      ? 'text-emerald-300 border-emerald-400/20 bg-emerald-500/10'
      : tone === 'warning'
        ? 'text-amber-300 border-amber-400/20 bg-amber-500/10'
        : 'text-slate-300 border-white/10 bg-white/[0.03]';

  return (
    <div className={`rounded-2xl border p-4 ${toneClass}`}>
      <div className="flex items-center gap-2 text-xs uppercase tracking-[0.14em]">
        <Icon size={14} />
        {label}
      </div>
      <p className="mt-2 text-sm font-medium text-white">{value}</p>
    </div>
  );
}

function VerificationCard({
  title,
  description,
  verified,
  challenge,
  code,
  requesting,
  confirming,
  onCodeChange,
  onRequest,
  onConfirm,
}: {
  title: string;
  description: string;
  verified: boolean;
  challenge: AccountVerificationChallenge | null;
  code: string;
  requesting: boolean;
  confirming: boolean;
  onCodeChange: (value: string) => void;
  onRequest: () => Promise<void>;
  onConfirm: () => Promise<void>;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-white">{title}</p>
          <p className="mt-1 text-xs leading-5 text-slate-400">{description}</p>
        </div>
        <span className={`rounded-full px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] ${verified ? 'border border-emerald-400/30 bg-emerald-500/15 text-emerald-300' : 'border border-amber-400/30 bg-amber-500/15 text-amber-300'}`}>
          {verified ? 'Verificado' : 'Pendente'}
        </span>
      </div>

      {verified ? (
        <p className="mt-3 text-xs text-emerald-300">Identidade confirmada com sucesso.</p>
      ) : (
        <>
          {challenge ? (
            <div className="mt-3 space-y-3">
              <div className="rounded-xl border border-cyan/20 bg-cyan/5 px-3 py-2 text-xs text-slate-200">
                <p>Código enviado para {challenge.destination}.</p>
                <p>Expira em {new Date(challenge.expires_at).toLocaleTimeString('pt-BR')}.</p>
                {challenge.preview_code ? <p className="mt-1 text-cyan">Prévia dev: {challenge.preview_code}</p> : null}
              </div>
              <div className="flex flex-col gap-2 sm:flex-row">
                <input
                  value={code}
                  onChange={(event) => onCodeChange(event.target.value)}
                  placeholder="Digite o código recebido"
                  className="w-full rounded-xl border border-white/10 bg-ink/60 px-4 py-2.5 text-sm text-white placeholder:text-slate-500 focus:border-cyan/50 focus:outline-none focus:ring-2 focus:ring-cyan/20"
                />
                <button
                  type="button"
                  onClick={() => void onConfirm()}
                  disabled={confirming || code.trim().length < 4}
                  className="rounded-xl bg-cyan px-4 py-2.5 text-sm font-semibold text-ink transition hover:bg-cyan/90 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {confirming ? 'Confirmando...' : 'Confirmar'}
                </button>
              </div>
            </div>
          ) : null}
          <button
            type="button"
            onClick={() => void onRequest()}
            disabled={requesting}
            className="mt-3 rounded-xl border border-white/15 px-4 py-2 text-sm font-semibold text-slate-100 transition hover:border-cyan/40 hover:text-white disabled:cursor-not-allowed disabled:opacity-50"
          >
            {requesting ? 'Gerando código...' : 'Enviar código'}
          </button>
        </>
      )}
    </div>
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
  const [profile, setProfile] = useState<AccountProfile | null>(null);
  const [form, setForm] = useState<AccountProfileUpdate | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [emailChallenge, setEmailChallenge] = useState<AccountVerificationChallenge | null>(null);
  const [phoneChallenge, setPhoneChallenge] = useState<AccountVerificationChallenge | null>(null);
  const [emailCode, setEmailCode] = useState('');
  const [phoneCode, setPhoneCode] = useState('');
  const [requestingEmail, setRequestingEmail] = useState(false);
  const [requestingPhone, setRequestingPhone] = useState(false);
  const [confirmingEmail, setConfirmingEmail] = useState(false);
  const [confirmingPhone, setConfirmingPhone] = useState(false);
  const savedTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

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
    void loadProfile();
  }, []);

  if (!form || !profile) {
    return (
      <div className="flex items-center gap-3 rounded-3xl border border-white/10 bg-white/[0.03] p-5 text-slate-300">
        <Loader2 size={16} className="animate-spin text-cyan-300" /> Carregando perfil...
      </div>
    );
  }

  const completionChecks = [
    { done: Boolean(form.avatar_url), label: 'Adicionar foto' },
    { done: Boolean(form.bio && form.bio.trim().length >= 20), label: 'Escrever bio' },
    { done: Boolean(form.company), label: 'Informar empresa' },
    { done: Boolean(form.job_title), label: 'Informar cargo' },
    { done: Boolean(form.timezone), label: 'Definir fuso horário' },
    { done: profile.phone_verified, label: 'Confirmar telefone' },
  ];
  const completedCount = completionChecks.filter((item) => item.done).length;
  const completionPercent = Math.round((completedCount / completionChecks.length) * 100);

  function formatDate(value: string | null) {
    if (!value) return 'Ainda não disponível';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return 'Ainda não disponível';
    return date.toLocaleString('pt-BR');
  }

  async function save() {
    const payload = form;
    if (!payload) return;

    setSaving(true);
    setSaved(false);
    try {
      const updatedProfile = await updateAccountProfile(payload);
      setProfile(updatedProfile);
      setForm({
        name: updatedProfile.name,
        username: updatedProfile.username,
        email: updatedProfile.email,
        phone: updatedProfile.phone,
        avatar_url: updatedProfile.avatar_url,
        bio: updatedProfile.bio,
        company: updatedProfile.company,
        job_title: updatedProfile.job_title,
        timezone: updatedProfile.timezone,
        language: updatedProfile.language,
      });
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

  async function handleEmailRequest() {
    setRequestingEmail(true);
    try {
      const challenge = await requestEmailVerification();
      setEmailChallenge(challenge);
      pushToast(challenge.message, 'success');
    } catch (err) {
      pushToast(err instanceof Error ? err.message : 'Erro ao solicitar verificação de email', 'error');
    } finally {
      setRequestingEmail(false);
    }
  }

  async function handlePhoneRequest() {
    setRequestingPhone(true);
    try {
      const challenge = await requestPhoneVerification();
      setPhoneChallenge(challenge);
      pushToast(challenge.message, 'success');
    } catch (err) {
      pushToast(err instanceof Error ? err.message : 'Erro ao solicitar verificação de telefone', 'error');
    } finally {
      setRequestingPhone(false);
    }
  }

  async function handleEmailConfirm() {
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

  async function handlePhoneConfirm() {
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

  return (
    <div className="space-y-5">
      {/* Header com avatar + identidade */}
      <ProfileHeader
        avatarUrl={form.avatar_url ?? null}
        name={form.name}
        username={form.username}
        planName={current?.plan_name ?? 'Free'}
        status={profile.status}
        onAvatarChange={(url) => setForm((cur) => (cur ? { ...cur, avatar_url: url } : cur))}
      />

      <div className="grid gap-5 xl:grid-cols-[1.4fr_0.9fr]">
        <FormSection title="Dados principais" description="Identidade básica e preferências de uso da conta.">
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
            <FormInput
              label="Idioma principal"
              value={form.language}
              onChange={(v) => setForm((cur) => (cur ? { ...cur, language: v } : cur))}
              placeholder="pt-BR"
            />
            <FormInput
              label="Fuso horário"
              value={form.timezone}
              onChange={(v) => setForm((cur) => (cur ? { ...cur, timezone: v } : cur))}
              placeholder="America/Sao_Paulo"
            />
          </div>
        </FormSection>

        <FormSection title="Completude do perfil" description="Quanto mais completo, melhor a identidade operacional da conta.">
          <div className="rounded-2xl border border-cyan/20 bg-cyan/5 p-4">
            <div className="flex items-center justify-between gap-3">
              <p className="text-sm font-semibold text-white">Perfil {completionPercent}% concluído</p>
              <span className="text-xs text-cyan">{completedCount}/{completionChecks.length}</span>
            </div>
            <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/10">
              <div className="h-full rounded-full bg-cyan transition-all" style={{ width: `${completionPercent}%` }} />
            </div>
          </div>
          <div className="space-y-2">
            {completionChecks.map((item) => (
              <div key={item.label} className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 text-sm">
                <span className="text-slate-200">{item.label}</span>
                <span className={item.done ? 'text-emerald-300' : 'text-amber-300'}>{item.done ? 'Concluído' : 'Pendente'}</span>
              </div>
            ))}
          </div>
        </FormSection>
      </div>

      <div className="grid gap-5 xl:grid-cols-[1.2fr_1fr]">
        <FormSection title="Conta e contexto profissional" description="Informações que dão contexto operacional à sua identidade na AXI.">
          <div className="grid gap-4 md:grid-cols-2">
            <FormInput
              label="Username"
              value={form.username}
              onChange={(v) => setForm((cur) => (cur ? { ...cur, username: v ?? '' } : cur))}
              placeholder="seu-username"
            />
            <FormInput
              label="Empresa"
              value={form.company}
              onChange={(v) => setForm((cur) => (cur ? { ...cur, company: v } : cur))}
              placeholder="Ex: AXI Labs"
            />
            <FormInput
              label="Função / Cargo"
              value={form.job_title}
              onChange={(v) => setForm((cur) => (cur ? { ...cur, job_title: v } : cur))}
              placeholder="Ex: Head de Operações"
            />
          </div>
          <div className="mt-4">
            <FormTextarea
              label="Bio"
              value={form.bio}
              onChange={(v) => setForm((cur) => (cur ? { ...cur, bio: v } : cur))}
              placeholder="Descreva em uma linha seu papel na operação, o que você constrói na AXI ou como usa a plataforma no dia a dia."
              maxLength={160}
            />
          </div>
        </FormSection>

        <FormSection title="Status da conta" description="Visão rápida do estado atual da sua conta e dos sinais de confiança.">
          <div className="grid gap-3">
            <StatusItem icon={Mail} label="Email verificado" value={profile.email_verified ? 'Sim, validado' : 'Não verificado'} tone={profile.email_verified ? 'success' : 'warning'} />
            <StatusItem icon={ShieldCheck} label="Telefone confirmado" value={profile.phone_verified ? 'Sim, confirmado' : 'Ainda não confirmado'} tone={profile.phone_verified ? 'success' : 'warning'} />
            <StatusItem icon={Clock3} label="Conta criada em" value={formatDate(profile.created_at)} />
            <StatusItem icon={AlertCircle} label="Último acesso" value={formatDate(profile.last_login_at)} />
            <StatusItem icon={BriefcaseBusiness} label="Plano atual" value={current?.plan_name ?? profile.plan} tone="success" />
            <StatusItem icon={UserCircle2} label="Status da conta" value={profile.status} tone="success" />
          </div>
        </FormSection>
      </div>

      <FormSection title="Verificações" description="Transforme os indicadores de confiança em ações reais da conta.">
        <div className="grid gap-4 lg:grid-cols-2">
          <VerificationCard
            title="Verificação de email"
            description="Gera um código temporário para confirmar que o endereço de email pertence a esta conta."
            verified={profile.email_verified}
            challenge={emailChallenge}
            code={emailCode}
            requesting={requestingEmail}
            confirming={confirmingEmail}
            onCodeChange={setEmailCode}
            onRequest={handleEmailRequest}
            onConfirm={handleEmailConfirm}
          />
          <VerificationCard
            title="Verificação de telefone"
            description="Confirma o telefone cadastrado e melhora a confiabilidade operacional da conta."
            verified={profile.phone_verified}
            challenge={phoneChallenge}
            code={phoneCode}
            requesting={requestingPhone}
            confirming={confirmingPhone}
            onCodeChange={setPhoneCode}
            onRequest={handlePhoneRequest}
            onConfirm={handlePhoneConfirm}
          />
        </div>
      </FormSection>

      <FormSection title="Resumo operacional" description="O que a plataforma sabe sobre esta conta hoje.">
        <div className="grid gap-4 md:grid-cols-3">
          <FormInput
            label="Plano"
            value={current?.plan_name ?? profile.plan}
            onChange={() => undefined}
            disabled
          />
          <FormInput label="Status" value={profile.status} onChange={() => undefined} disabled />
          <FormInput label="Atualizado em" value={formatDate(profile.updated_at)} onChange={() => undefined} disabled />
        </div>
      </FormSection>

      {/* Ações */}
      <div className="flex items-center justify-end gap-3 pt-2">
        <button
          type="button"
          onClick={() => {
            void loadProfile();
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
