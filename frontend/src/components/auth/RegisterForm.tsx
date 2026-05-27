import { FormEvent, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { useAuth } from '../../hooks/useAuth';
import { startGoogleLogin } from '../../services/auth.service';

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
      navigate('/app/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao cadastrar');
    }
  }

  return (
    <div className="space-y-5">
      <button
        type="button"
        onClick={startGoogleLogin}
        className="flex w-full items-center justify-center gap-3 rounded-2xl border border-white/15 bg-white px-4 py-3 font-semibold text-slate-950 transition hover:bg-slate-100"
      >
        <span className="grid h-6 w-6 place-items-center rounded-full bg-gradient-to-br from-blue-500 via-red-500 to-yellow-400 text-xs font-black text-white">G</span>
        Cadastrar com Google
      </button>

      <div className="flex items-center gap-3 text-xs uppercase tracking-[0.24em] text-slate-500">
        <span className="h-px flex-1 bg-white/10" />
        ou email
        <span className="h-px flex-1 bg-white/10" />
      </div>

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
          {loading ? 'Criando conta...' : 'Criar conta com email'}
        </button>
      </form>

      <p className="text-center text-sm text-slate-400">
        Já tem conta? <Link to="/login" className="font-semibold text-cyan hover:text-white">Entrar</Link>
      </p>
    </div>
  );
}
