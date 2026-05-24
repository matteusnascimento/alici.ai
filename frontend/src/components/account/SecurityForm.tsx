import { Check, Eye, EyeOff, KeyRound, Loader2, ShieldCheck } from 'lucide-react';
import { useRef, useState } from 'react';

import { useToast } from '../../hooks/useToast';
import type { AccountChangePasswordPayload } from '../../types/account';

interface SecurityFormProps {
  onSubmit: (payload: AccountChangePasswordPayload) => Promise<void>;
  loading: boolean;
}

function passwordStrength(pwd: string): { score: number; label: string; color: string } {
  if (!pwd) return { score: 0, label: '', color: '' };
  let score = 0;
  if (pwd.length >= 8) score++;
  if (pwd.length >= 12) score++;
  if (/[A-Z]/.test(pwd)) score++;
  if (/[0-9]/.test(pwd)) score++;
  if (/[^A-Za-z0-9]/.test(pwd)) score++;
  if (score <= 1) return { score, label: 'Fraca', color: 'bg-rose-400' };
  if (score <= 3) return { score, label: 'Média', color: 'bg-amber-400' };
  return { score, label: 'Forte', color: 'bg-emerald-400' };
}

export function SecurityForm({ onSubmit, loading }: SecurityFormProps) {
  const { pushToast } = useToast();
  const [form, setForm] = useState<AccountChangePasswordPayload>({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });
  const [showPwd, setShowPwd] = useState(false);
  const [saved, setSaved] = useState(false);
  const savedTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const strength = passwordStrength(form.new_password);
  const mismatch = form.confirm_password.length > 0 && form.confirm_password !== form.new_password;

  async function handleSave() {
    if (form.new_password.length < 8) {
      pushToast('Nova senha deve ter ao menos 8 caracteres.', 'error');
      return;
    }
    if (form.new_password !== form.confirm_password) {
      pushToast('Confirmação de senha diferente.', 'error');
      return;
    }
    try {
      await onSubmit(form);
      setSaved(true);
      pushToast('Senha alterada com sucesso.', 'success');
      setForm({ current_password: '', new_password: '', confirm_password: '' });
      if (savedTimer.current) clearTimeout(savedTimer.current);
      savedTimer.current = setTimeout(() => setSaved(false), 2500);
    } catch (err) {
      pushToast(err instanceof Error ? err.message : 'Falha ao alterar senha', 'error');
    }
  }

  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
      <div className="mb-5 flex items-center gap-3">
        <ShieldCheck size={20} className="text-cyan-300" />
        <div>
          <h2 className="font-display text-2xl text-white">Alterar Senha</h2>
          <p className="mt-0.5 text-sm text-slate-400">Use uma senha forte com ao menos 8 caracteres.</p>
        </div>
      </div>

      <div className="space-y-4">
        <label className="block space-y-1.5 text-sm">
          <span className="font-medium text-slate-300">Senha atual</span>
          <input
            type="password"
            value={form.current_password}
            onChange={(e) => setForm((f) => ({ ...f, current_password: e.target.value }))}
            className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white transition focus:border-cyan/50 focus:outline-none focus:ring-2 focus:ring-cyan/20"
          />
        </label>

        <label className="block space-y-1.5 text-sm">
          <span className="font-medium text-slate-300">Nova senha</span>
          <div className="relative">
            <input
              type={showPwd ? 'text' : 'password'}
              value={form.new_password}
              onChange={(e) => setForm((f) => ({ ...f, new_password: e.target.value }))}
              className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 pr-12 text-white transition focus:border-cyan/50 focus:outline-none focus:ring-2 focus:ring-cyan/20"
            />
            <button
              type="button"
              onClick={() => setShowPwd((v) => !v)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-200"
            >
              {showPwd ? <EyeOff size={16} /> : <Eye size={16} />}
            </button>
          </div>
          {strength.label && (
            <div className="mt-1.5">
              <div className="flex gap-1">
                {[1, 2, 3, 4, 5].map((n) => (
                  <div
                    key={n}
                    className={`h-1 flex-1 rounded-full transition-all duration-200 ${
                      n <= strength.score ? strength.color : 'bg-white/10'
                    }`}
                  />
                ))}
              </div>
              <span className={`mt-1 text-xs ${
                strength.score <= 1 ? 'text-rose-300' : strength.score <= 3 ? 'text-amber-300' : 'text-emerald-300'
              }`}>{strength.label}</span>
            </div>
          )}
        </label>

        <label className="block space-y-1.5 text-sm">
          <span className="font-medium text-slate-300">Confirmar nova senha</span>
          <input
            type="password"
            value={form.confirm_password}
            onChange={(e) => setForm((f) => ({ ...f, confirm_password: e.target.value }))}
            className={`w-full rounded-2xl border bg-ink/60 px-4 py-3 text-white transition focus:outline-none focus:ring-2 ${
              mismatch
                ? 'border-rose-400/50 focus:border-rose-400/70 focus:ring-rose-400/20'
                : 'border-white/10 focus:border-cyan/50 focus:ring-cyan/20'
            }`}
          />
          {mismatch && <p className="text-xs text-rose-300">Senhas não conferem</p>}
        </label>
      </div>

      <button
        type="button"
        disabled={loading}
        onClick={() => void handleSave()}
        className={`mt-5 inline-flex items-center gap-2 rounded-2xl px-5 py-2.5 text-sm font-semibold transition ${
          saved
            ? 'border border-emerald-400/40 bg-emerald-500/15 text-emerald-300'
            : 'bg-sand text-ink hover:bg-sand/90 disabled:opacity-60'
        }`}
      >
        {loading ? <Loader2 size={15} className="animate-spin" /> : saved ? <Check size={15} /> : <KeyRound size={15} />}
        {loading ? 'Salvando…' : saved ? 'Senha atualizada!' : 'Atualizar senha'}
      </button>
    </section>
  );
}
