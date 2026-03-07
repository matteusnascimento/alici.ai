const actions = [
  "Criar novo agente",
  "Abrir AI Playground",
  "Conectar integracao",
  "Exportar relatorio"
];

export function QuickActions() {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
      <h3 className="text-sm font-semibold text-slate-200">Quick Actions</h3>
      <div className="mt-4 grid gap-3">
        {actions.map((action) => (
          <button
            key={action}
            type="button"
            className="rounded-lg border border-slate-700 px-4 py-3 text-left text-sm text-slate-200 hover:border-sky-400 hover:bg-slate-800"
          >
            {action}
          </button>
        ))}
      </div>
    </section>
  );
}
