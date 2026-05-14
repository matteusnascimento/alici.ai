import { useState } from 'react';

interface AgentManualKnowledgeFormProps {
  busy?: boolean;
  onSave: (payload: { title: string; content: string }) => Promise<void>;
}

export function AgentManualKnowledgeForm({ busy = false, onSave }: AgentManualKnowledgeFormProps) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  async function handleSave() {
    if (!title.trim() || !content.trim() || busy) return;
    await onSave({ title: title.trim(), content: content.trim() });
    setTitle('');
    setContent('');
  }

  return (
    <section className="rounded-3xl border border-white/10 bg-gradient-to-b from-white/[0.09] to-white/[0.03] p-5 shadow-soft">
      <h2 className="font-display text-lg text-white">Conteudo manual</h2>
      <p className="mt-1 text-sm text-slate-300">Adicione instrucoes e contexto que devem guiar as respostas do agente.</p>

      <div className="mt-4 space-y-3">
        <input
          value={title}
          onChange={(event) => setTitle(event.target.value)}
          placeholder="Titulo do conteudo"
          className="w-full rounded-xl border border-white/15 bg-black/25 px-3 py-2 text-sm text-white outline-none transition focus:border-cyan/55"
        />
        <textarea
          value={content}
          onChange={(event) => setContent(event.target.value)}
          placeholder="Escreva o conhecimento base que o agente deve utilizar"
          className="min-h-32 w-full rounded-xl border border-white/15 bg-black/25 px-3 py-2 text-sm text-white outline-none transition focus:border-cyan/55"
        />
      </div>

      <div className="mt-4 flex justify-end">
        <button
          type="button"
          onClick={() => void handleSave()}
          disabled={!title.trim() || !content.trim() || busy}
          className="rounded-xl border border-white/20 bg-white/[0.06] px-4 py-2 text-sm font-medium text-slate-100 transition hover:border-cyan/50 hover:text-white disabled:cursor-not-allowed disabled:opacity-60"
        >
          {busy ? 'Salvando...' : 'Salvar conteudo'}
        </button>
      </div>
    </section>
  );
}
