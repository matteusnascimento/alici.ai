import { Link } from 'react-router-dom';

export function BillingCancelPage() {
  return (
    <section className="mx-auto max-w-2xl rounded-3xl border border-amber-400/30 bg-amber-500/5 p-8">
      <p className="text-xs uppercase tracking-[0.2em] text-amber-300">Checkout cancelado</p>
      <h1 className="mt-2 font-display text-3xl text-white">Nenhuma cobrança foi realizada</h1>
      <p className="mt-3 text-sm text-slate-300">
        Você pode revisar os planos e tentar novamente quando quiser.
      </p>
      <div className="mt-6">
        <Link
          to="/app/account/overview"
          className="rounded-2xl border border-white/20 px-4 py-2 text-sm font-semibold text-white transition hover:border-amber-300/60 hover:text-amber-200"
        >
          Voltar para assinatura
        </Link>
      </div>
    </section>
  );
}
