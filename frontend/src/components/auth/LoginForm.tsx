import { FormEvent, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { useAuth } from '../../hooks/useAuth';

export function LoginForm() {
  const navigate = useNavigate();
  const { login, loading } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    try {
      await login({ email, password });
      navigate('/app/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao autenticar');
    }
  }

  return (
    <form className="space-y-5" onSubmit={handleSubmit}>
      <div>
        <label className="mb-2 block text-sm font-medium text-slate-200">Email</label>
        <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none focus:border-cyan" type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
      </div>
      <div>
        <label className="mb-2 block text-sm font-medium text-slate-200">Senha</label>
        <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none focus:border-cyan" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required />
      </div>
      {error ? <p className="text-sm text-coral">{error}</p> : null}
      <button className="w-full rounded-2xl bg-sand px-4 py-3 font-semibold text-ink transition hover:bg-white disabled:opacity-60" disabled={loading} type="submit">
        {loading ? 'Entrando...' : 'Entrar'}
      </button>
    </form>
  );
}
