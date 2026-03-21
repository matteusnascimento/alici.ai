import { FormEvent, useState } from 'react';

import { useAgents } from '../../hooks/useAgents';

const initialForm = {
  nome: '',
  funcao: '',
  tipo: 'vendas',
  linguagem: 'pt-BR',
  prompt: '',
  whatsapp: '',
  instagram: '',
  api: '',
  outros: '',
  outros_nome: '',
  ativo: true,
};

export function AgentsPanel() {
  const { agents, loading, saving, error, addAgent, handleToggle } = useAgents();
  const [form, setForm] = useState(initialForm);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await addAgent(form);
    setForm(initialForm);
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
      <section className="panel-base">
        <h3 className="font-display text-2xl text-white">Criar agente</h3>
        <form className="mt-6 grid gap-4 md:grid-cols-2" onSubmit={handleSubmit}>
          {[
            ['nome', 'Nome'],
            ['funcao', 'Função'],
            ['tipo', 'Tipo'],
            ['linguagem', 'Linguagem'],
            ['whatsapp', 'WhatsApp'],
            ['instagram', 'Instagram'],
            ['api', 'API'],
            ['outros', 'Outros'],
            ['outros_nome', 'Nome do outro canal'],
          ].map(([key, label]) => (
            <div key={key} className={key === 'outros_nome' ? 'md:col-span-2' : ''}>
              <label className="mb-2 block text-sm text-slate-300">{label}</label>
              <input
                className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none focus:border-cyan"
                value={form[key as keyof typeof form] as string}
                onChange={(event) => setForm((current) => ({ ...current, [key]: event.target.value }))}
                required={['nome', 'funcao', 'tipo', 'linguagem'].includes(key)}
              />
            </div>
          ))}
          <div className="md:col-span-2">
            <label className="mb-2 block text-sm text-slate-300">Prompt</label>
            <textarea className="min-h-32 w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none focus:border-cyan" value={form.prompt} onChange={(event) => setForm((current) => ({ ...current, prompt: event.target.value }))} required />
          </div>
          <button className="rounded-2xl bg-sand px-4 py-3 font-semibold text-ink transition hover:bg-white disabled:opacity-60 md:col-span-2" disabled={saving} type="submit">
            {saving ? 'Salvando agente...' : 'Criar agente'}
          </button>
        </form>
        {error ? <p className="mt-4 text-sm text-coral">{error}</p> : null}
      </section>
      <section className="panel-base">
        <div className="flex items-center justify-between">
          <h3 className="font-display text-2xl text-white">Seus agentes</h3>
          <span className="rounded-full border border-white/10 px-3 py-1 text-sm text-slate-200">{agents.length} total</span>
        </div>
        <div className="mt-6 space-y-4">
          {loading ? <p className="text-slate-300">Carregando agentes...</p> : null}
          {!loading && agents.length === 0 ? <p className="text-slate-300">Nenhum agente criado ainda.</p> : null}
          {agents.map((agent) => (
            <article key={agent.id} className="rounded-3xl border border-white/10 bg-white/5 p-5">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <p className="font-display text-2xl text-white">{agent.nome}</p>
                  <p className="mt-2 text-slate-300">{agent.funcao}</p>
                  <p className="mt-3 text-sm text-slate-400">{agent.tipo} • {agent.linguagem}</p>
                </div>
                <button className={`rounded-full px-4 py-2 text-sm font-semibold ${agent.ativo ? 'bg-cyan text-ink' : 'border border-white/10 text-white'}`} onClick={() => handleToggle(agent.id)} type="button">
                  {agent.ativo ? 'Ativo' : 'Inativo'}
                </button>
              </div>
              <p className="mt-4 text-slate-300">{agent.prompt}</p>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
