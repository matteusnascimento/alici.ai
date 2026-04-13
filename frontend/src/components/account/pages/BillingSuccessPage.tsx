import { useEffect } from 'react';
import { Link } from 'react-router-dom';

import { useBilling } from '../../../hooks/useBilling';

export function BillingSuccessPage() {
  const { reload } = useBilling();

  useEffect(() => {
    void reload();
  }, [reload]);

  return (
    <section className="mx-auto max-w-2xl rounded-3xl border border-emerald-400/30 bg-emerald-500/5 p-8">
      <p className="text-xs uppercase tracking-[0.2em] text-emerald-300">Pagamento aprovado</p>
      <h1 className="mt-2 font-display text-3xl text-white">Assinatura atualizada com sucesso</h1>
      <p className="mt-3 text-sm text-slate-300">
        O Stripe confirmou o checkout. Os dados da assinatura serão sincronizados automaticamente via webhook.
      </p>
      <div className="mt-6 flex flex-wrap gap-3">
        <Link
          to="/app/account/overview"
          className="rounded-2xl bg-emerald-300 px-4 py-2 text-sm font-semibold text-ink transition hover:bg-emerald-200"
        >
          Voltar para conta
        </Link>
        <Link
          to="/app/dashboard"
          className="rounded-2xl border border-white/20 px-4 py-2 text-sm font-semibold text-white transition hover:border-emerald-300/60 hover:text-emerald-200"
        >
          Ir para dashboard
        </Link>
      </div>
    </section>
  );
}
