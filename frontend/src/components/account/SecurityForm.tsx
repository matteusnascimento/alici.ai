import { useState } from 'react';

import type { AccountChangePasswordPayload } from '../../types/account';

interface SecurityFormProps {
  onSubmit: (payload: AccountChangePasswordPayload) => Promise<void>;
  loading: boolean;
}

export function SecurityForm({ onSubmit, loading }: SecurityFormProps) {
  const [form, setForm] = useState<AccountChangePasswordPayload>({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleSave() {
    setError(null);
    setMessage(null);
    if (form.new_password.length < 8) {
      setError('Nova senha deve ter ao menos 8 caracteres.');
      return;
    }
    if (form.new_password !== form.confirm_password) {
      setError('Confirmacao de senha diferente.');
      return;
    }
    try {
      await onSubmit(form);
      setMessage('Senha alterada com sucesso.');
      setForm({ current_password: '', new_password: '', confirm_password: '' });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao alterar senha');
    }
  }

  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
      <h2 className="font-display text-2xl text-white">Security</h2>
      <div className="mt-4 space-y-3">
        {[
          ['current_password', 'Senha atual'],
          ['new_password', 'Nova senha'],
          ['confirm_password', 'Confirmar nova senha'],
        ].map(([key, label]) => (
          <label key={key} className="block space-y-2 text-sm text-slate-300">
            <span>{label}</span>
            <input
              type="password"
              value={form[key as keyof AccountChangePasswordPayload]}
              onChange={(event) => setForm((current) => ({ ...current, [key]: event.target.value }))}
              className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white"
            />
          </label>
        ))}
      </div>
      <button type="button" disabled={loading} onClick={handleSave} className="mt-4 rounded-2xl bg-sand px-4 py-2 text-sm font-semibold text-ink">
        {loading ? 'Salvando...' : 'Atualizar senha'}
      </button>
      {message ? <p className="mt-3 text-sm text-cyan">{message}</p> : null}
      {error ? <p className="mt-3 text-sm text-coral">{error}</p> : null}
    </section>
  );
}
