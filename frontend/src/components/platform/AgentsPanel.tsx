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
  const {
    agents,
    loading,
    saving,
    working,
    error,
    selectedAgentId,
    channels,
    knowledge,
    actions,
    logs,
    analytics,
    lastTest,
    addAgent,
    handleToggle,
    selectAgent,
    addChannel,
    addKnowledge,
    addAction,
    runAgentTest,
  } = useAgents();
  const [form, setForm] = useState(initialForm);
  const [channelForm, setChannelForm] = useState({
    channel_type: 'website',
    provider_name: 'internal',
    channel_id: '',
    external_account_id: '',
    credential_ref: '',
  });
  const [knowledgeForm, setKnowledgeForm] = useState({
    title: '',
    kind: 'faq',
    content: '',
    tags: '',
  });
  const [actionForm, setActionForm] = useState({
    name: '',
    action_type: 'save_lead',
    trigger_keywords: '',
  });
  const [testInput, setTestInput] = useState('');

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await addAgent(form);
    setForm(initialForm);
  }

  async function handleCreateChannel(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await addChannel({
      ...channelForm,
      external_account_id: channelForm.external_account_id || undefined,
      credential_ref: channelForm.credential_ref || undefined,
      config: {},
    });
    setChannelForm((current) => ({ ...current, channel_id: '', external_account_id: '', credential_ref: '' }));
  }

  async function handleCreateKnowledge(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await addKnowledge({
      ...knowledgeForm,
      tags: knowledgeForm.tags || undefined,
    });
    setKnowledgeForm({ title: '', kind: 'faq', content: '', tags: '' });
  }

  async function handleCreateAction(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await addAction({
      ...actionForm,
      trigger_keywords: actionForm.trigger_keywords || undefined,
      config: {},
    });
    setActionForm({ name: '', action_type: 'save_lead', trigger_keywords: '' });
  }

  async function handleRunTest(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!testInput.trim()) return;
    await runAgentTest(testInput);
    setTestInput('');
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
            <article key={agent.id} className={`rounded-3xl border p-5 ${selectedAgentId === agent.id ? 'border-cyan bg-cyan/10' : 'border-white/10 bg-white/5'}`}>
              <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div>
                  <p className="font-display text-2xl text-white">{agent.nome}</p>
                  <p className="mt-2 text-slate-300">{agent.funcao}</p>
                  <p className="mt-3 text-sm text-slate-400">{agent.tipo} • {agent.linguagem}</p>
                </div>
                <div className="flex gap-2">
                  <button className="rounded-full border border-white/10 px-4 py-2 text-sm text-white" onClick={() => void selectAgent(agent.id)} type="button">
                    Operar
                  </button>
                  <button className={`rounded-full px-4 py-2 text-sm font-semibold ${agent.ativo ? 'bg-cyan text-ink' : 'border border-white/10 text-white'}`} onClick={() => void handleToggle(agent.id)} type="button">
                    {agent.ativo ? 'Ativo' : 'Inativo'}
                  </button>
                </div>
              </div>
              <p className="mt-4 text-slate-300">{agent.prompt}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="panel-base xl:col-span-2">
        <h3 className="font-display text-2xl text-white">Operacao em tempo real</h3>
        {!selectedAgentId ? <p className="mt-4 text-slate-300">Selecione um agente para operar canais, conhecimento, acoes, testes e analytics.</p> : null}
        {selectedAgentId ? (
          <div className="mt-6 grid gap-6 lg:grid-cols-2">
            <article className="rounded-3xl border border-white/10 bg-white/5 p-5">
              <h4 className="font-display text-xl text-white">Canais</h4>
              <form className="mt-4 grid gap-3" onSubmit={handleCreateChannel}>
                <input className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white" value={channelForm.channel_type} onChange={(event) => setChannelForm((current) => ({ ...current, channel_type: event.target.value }))} placeholder="channel_type" required />
                <input className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white" value={channelForm.provider_name} onChange={(event) => setChannelForm((current) => ({ ...current, provider_name: event.target.value }))} placeholder="provider_name" required />
                <input className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white" value={channelForm.channel_id} onChange={(event) => setChannelForm((current) => ({ ...current, channel_id: event.target.value }))} placeholder="channel_id" required />
                <button className="rounded-2xl bg-sand px-4 py-3 font-semibold text-ink" disabled={working} type="submit">Adicionar canal</button>
              </form>
              <div className="mt-4 space-y-2 text-sm text-slate-300">
                {channels.map((item) => (
                  <p key={item.id}>{item.channel_type} • {item.provider_name} • {item.channel_id}</p>
                ))}
              </div>
            </article>

            <article className="rounded-3xl border border-white/10 bg-white/5 p-5">
              <h4 className="font-display text-xl text-white">Base de conhecimento</h4>
              <form className="mt-4 grid gap-3" onSubmit={handleCreateKnowledge}>
                <input className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white" value={knowledgeForm.title} onChange={(event) => setKnowledgeForm((current) => ({ ...current, title: event.target.value }))} placeholder="titulo" required />
                <input className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white" value={knowledgeForm.kind} onChange={(event) => setKnowledgeForm((current) => ({ ...current, kind: event.target.value }))} placeholder="tipo" required />
                <textarea className="min-h-24 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white" value={knowledgeForm.content} onChange={(event) => setKnowledgeForm((current) => ({ ...current, content: event.target.value }))} placeholder="conteudo" required />
                <button className="rounded-2xl bg-sand px-4 py-3 font-semibold text-ink" disabled={working} type="submit">Adicionar conhecimento</button>
              </form>
              <div className="mt-4 space-y-2 text-sm text-slate-300">
                {knowledge.map((item) => (
                  <p key={item.id}>{item.kind} • {item.title}</p>
                ))}
              </div>
            </article>

            <article className="rounded-3xl border border-white/10 bg-white/5 p-5">
              <h4 className="font-display text-xl text-white">Acoes</h4>
              <form className="mt-4 grid gap-3" onSubmit={handleCreateAction}>
                <input className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white" value={actionForm.name} onChange={(event) => setActionForm((current) => ({ ...current, name: event.target.value }))} placeholder="nome" required />
                <input className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white" value={actionForm.action_type} onChange={(event) => setActionForm((current) => ({ ...current, action_type: event.target.value }))} placeholder="tipo da acao" required />
                <input className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white" value={actionForm.trigger_keywords} onChange={(event) => setActionForm((current) => ({ ...current, trigger_keywords: event.target.value }))} placeholder="palavras-chave (csv)" />
                <button className="rounded-2xl bg-sand px-4 py-3 font-semibold text-ink" disabled={working} type="submit">Adicionar acao</button>
              </form>
              <div className="mt-4 space-y-2 text-sm text-slate-300">
                {actions.map((item) => (
                  <p key={item.id}>{item.action_type} • {item.name}</p>
                ))}
              </div>
            </article>

            <article className="rounded-3xl border border-white/10 bg-white/5 p-5">
              <h4 className="font-display text-xl text-white">Teste de runtime</h4>
              <form className="mt-4 grid gap-3" onSubmit={handleRunTest}>
                <textarea className="min-h-24 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white" value={testInput} onChange={(event) => setTestInput(event.target.value)} placeholder="Digite uma mensagem para o agente" required />
                <button className="rounded-2xl bg-cyan px-4 py-3 font-semibold text-ink" disabled={working} type="submit">Executar teste</button>
              </form>
              {lastTest ? (
                <div className="mt-4 rounded-2xl border border-cyan/40 bg-cyan/10 p-4 text-sm text-slate-100">
                  <p>Status: {lastTest.status}</p>
                  <p className="mt-2">Resposta: {lastTest.response}</p>
                </div>
              ) : null}
            </article>

            <article className="rounded-3xl border border-white/10 bg-white/5 p-5">
              <h4 className="font-display text-xl text-white">Analytics</h4>
              {!analytics ? <p className="mt-3 text-slate-300">Sem dados.</p> : (
                <div className="mt-4 grid grid-cols-2 gap-3 text-sm text-slate-200">
                  <p>Inbound: {analytics.total_inbound_messages}</p>
                  <p>Outbound: {analytics.total_outbound_messages}</p>
                  <p>Conversas: {analytics.total_conversations}</p>
                  <p>Ativas: {analytics.active_conversations}</p>
                  <p>Handoffs: {analytics.human_handoffs}</p>
                  <p>Leads: {analytics.leads_captured}</p>
                </div>
              )}
            </article>

            <article className="rounded-3xl border border-white/10 bg-white/5 p-5">
              <h4 className="font-display text-xl text-white">Logs recentes</h4>
              <div className="mt-4 max-h-60 space-y-2 overflow-auto text-sm text-slate-300">
                {logs.slice(0, 20).map((item) => (
                  <p key={item.id}>{item.event_type} • {item.status} • {item.summary}</p>
                ))}
              </div>
            </article>
          </div>
        ) : null}
        {error ? <p className="mt-4 text-sm text-coral">{error}</p> : null}
      </section>
    </div>
  );
}
