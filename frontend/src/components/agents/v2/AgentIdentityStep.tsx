interface AgentIdentityStepProps {
  data: {
    nome: string;
    funcao: string;
    linguagem: string;
    tone: string;
  };
  onChange: (next: Partial<AgentIdentityStepProps['data']>) => void;
}

const roleTemplates = ['Atendimento', 'Vendas', 'Captacao de Leads', 'Reservas', 'Suporte', 'Pos-venda', 'Marketing', 'Agendamento'];

export function AgentIdentityStep({ data, onChange }: AgentIdentityStepProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      <div>
        <label className="text-sm text-slate-300">Nome do agente</label>
        <input value={data.nome} onChange={(event) => onChange({ nome: event.target.value })} className="mt-2 w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-white" />
      </div>
      <div>
        <label className="text-sm text-slate-300">Idioma</label>
        <input value={data.linguagem} onChange={(event) => onChange({ linguagem: event.target.value })} className="mt-2 w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-white" />
      </div>
      <div className="md:col-span-2">
        <p className="text-sm text-slate-300">Funcao do agente</p>
        <div className="mt-2 flex flex-wrap gap-2">
          {roleTemplates.map((role) => (
            <button key={role} type="button" onClick={() => onChange({ funcao: role })} className={`rounded-xl border px-3 py-2 text-sm ${data.funcao === role ? 'border-cyan-300/40 bg-cyan-500/15 text-cyan-100' : 'border-white/20 text-slate-200'}`}>
              {role}
            </button>
          ))}
        </div>
      </div>
      <div className="md:col-span-2">
        <label className="text-sm text-slate-300">Tom de voz</label>
        <input value={data.tone} onChange={(event) => onChange({ tone: event.target.value })} className="mt-2 w-full rounded-xl border border-white/10 bg-white/5 px-3 py-2 text-white" />
      </div>
      <p className="md:col-span-2 rounded-2xl border border-cyan-300/25 bg-cyan-500/10 px-4 py-3 text-sm text-cyan-100">
        Este agente vai atuar como {data.funcao || '...'} para o seu negocio.
      </p>
    </div>
  );
}
