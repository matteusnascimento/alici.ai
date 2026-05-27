import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Loader2 } from 'lucide-react';

import { useAuth } from '../../hooks/useAuth';

export function GoogleOAuthCallback() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const { completeOAuthLogin } = useAuth();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function finish() {
      const providerError = params.get('error');
      const accessToken = params.get('access_token');
      const refreshToken = params.get('refresh_token') || undefined;
      const tokenType = params.get('token_type') || 'bearer';

      if (providerError) {
        setError('O Google recusou ou cancelou o login. Tente novamente.');
        return;
      }

      if (!accessToken) {
        setError('Não recebemos o token do Google. Tente entrar novamente.');
        return;
      }

      try {
        await completeOAuthLogin({ access_token: accessToken, refresh_token: refreshToken, token_type: tokenType });
        navigate('/app/dashboard', { replace: true });
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Falha ao concluir login com Google.');
      }
    }

    void finish();
  }, [completeOAuthLogin, navigate, params]);

  return (
    <main className="flex min-h-screen items-center justify-center bg-ink px-6 text-white">
      <section className="w-full max-w-md rounded-[2rem] border border-white/10 bg-white/5 p-8 text-center shadow-soft">
        {error ? (
          <>
            <p className="text-sm font-semibold uppercase tracking-[0.3em] text-coral">Login Google</p>
            <h1 className="mt-4 font-display text-3xl">Não foi possível entrar</h1>
            <p className="mt-3 text-sm text-slate-300">{error}</p>
            <button
              type="button"
              onClick={() => navigate('/login', { replace: true })}
              className="mt-6 rounded-2xl bg-sand px-5 py-3 text-sm font-semibold text-ink"
            >
              Voltar para login
            </button>
          </>
        ) : (
          <>
            <Loader2 className="mx-auto h-8 w-8 animate-spin text-cyan" />
            <h1 className="mt-5 font-display text-3xl">Entrando com Google</h1>
            <p className="mt-3 text-sm text-slate-300">Estamos validando sua conta e preparando o AXI.</p>
          </>
        )}
      </section>
    </main>
  );
}
