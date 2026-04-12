import { Link } from 'react-router-dom';

export function AccountAppsStatusPage() {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
      <p className="text-xs uppercase tracking-[0.24em] text-cyan-300">Conta AXI</p>
      <h2 className="mt-2 font-display text-2xl text-white">Status das conexoes</h2>
      <p className="mt-2 text-sm text-slate-300">
        Acompanhe a saude das integracoes e confira o estado mais recente de sincronizacao dos apps conectados.
      </p>

      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
          <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Diagnostico</p>
          <p className="mt-1 text-sm text-slate-200">Verifique falhas, latencia e disponibilidade das conexoes.</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-black/20 p-4">
          <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Sincronizacao</p>
          <p className="mt-1 text-sm text-slate-200">Confirme quando cada integracao atualizou pela ultima vez.</p>
        </div>
      </div>

      <div className="mt-5">
        <Link to="/app/account/apps" className="inline-flex rounded-xl border border-white/20 px-4 py-2 text-sm text-white hover:border-cyan-300/50">
          Abrir painel de aplicativos
        </Link>
      </div>
    </section>
  );
}
