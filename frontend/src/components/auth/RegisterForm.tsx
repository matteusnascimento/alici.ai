import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { useAuth } from '../../hooks/useAuth';

export function RegisterForm() {
  const navigate = useNavigate();
  const { register, loading } = useAuth();
  const [form, setForm] = useState({
    name: '',
    username: '',
    email: '',
    phone: '',
    password: '',
  });
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      await register(form);
      navigate('/app/revenue?view=business-pulse');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao cadastrar');
    }
  }

  return (
    <form className="space-y-5" onSubmit={handleSubmit}>
      {[
        ['name', 'Nome', 'text'],
        ['username', 'Username', 'text'],
        ['email', 'Email', 'email'],
        ['phone', 'Telefone', 'text'],
        ['password', 'Senha', 'password'],
      ].map(([key, label, type]) => (
        <div key={key}>
          <label className="mb-2 block text-sm font-medium text-slate-200">{label}</label>
          <input
            className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none focus:border-cyan"
            type={type}
            value={form[key as keyof typeof form]}
            onChange={(event) => setForm((current) => ({ ...current, [key]: event.target.value }))}
            required={key !== 'phone'}
          />
        </div>
      ))}
      {error ? <p className="text-sm text-coral">{error}</p> : null}
      <button className="w-full rounded-2xl bg-sand px-4 py-3 font-semibold text-ink transition hover:bg-white disabled:opacity-60" disabled={loading} type="submit">
        {loading ? 'Criando conta...' : 'Criar conta'}
      </button>
    </form>
  );
}
