import { Link } from 'react-router-dom';

export function AgentCreationSuccessState() {
  return (
    <section className="rounded-3xl border border-emerald-300/30 bg-[linear-gradient(135deg,rgba(6,78,59,0.45),rgba(8,47,73,0.55))] p-5">
      <p className="text-xs uppercase tracking-[0.18em] text-emerald-200">Agente criado com sucesso</p>
      <h2 className="mt-1 font-display text-3xl text-white">Seu agente foi criado.</h2>
      <p className="mt-2 text-sm text-emerald-100">
        Agora vamos configura-lo para comecar a trabalhar no seu negocio.
      </p>
      <div className="mt-4 grid gap-2 md:grid-cols-5">
        {['Conectar canais', 'Adicionar conhecimento', 'Definir acoes', 'Fazer teste', 'Ativar agente'].map((step) => (
          <div key={step} className="rounded-xl border border-white/15 bg-white/5 px-3 py-2 text-xs text-slate-100">
            {step}
          </div>
        ))}
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        <Link to="#onboarding" className="rounded-xl bg-emerald-300 px-4 py-2 text-sm font-semibold text-emerald-950">
          Continuar configuracao
        </Link>
        <Link to="#overview" className="rounded-xl border border-white/20 px-4 py-2 text-sm text-slate-100">
          Ver visao geral
        </Link>
      </div>
    </section>
  );
}
