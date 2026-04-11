import { useState } from 'react';

interface AgentFaqManagerProps {
  busy?: boolean;
  onAddFaq: (question: string, answer: string) => Promise<void>;
}

export function AgentFaqManager({ busy = false, onAddFaq }: AgentFaqManagerProps) {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  async function handleAddFaq() {
    if (!question.trim() || !answer.trim() || busy) return;
    await onAddFaq(question.trim(), answer.trim());
    setQuestion('');
    setAnswer('');
  }

  return (
    <section className="rounded-3xl border border-white/10 bg-gradient-to-b from-white/[0.09] to-white/[0.03] p-5 shadow-soft">
      <h2 className="font-display text-lg text-white">FAQ do agente</h2>
      <p className="mt-1 text-sm text-slate-300">Cadastre perguntas e respostas que o agente deve priorizar.</p>

      <div className="mt-4 space-y-3">
        <input
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Pergunta frequente"
          className="w-full rounded-xl border border-white/15 bg-black/25 px-3 py-2 text-sm text-white outline-none transition focus:border-cyan/55"
        />
        <textarea
          value={answer}
          onChange={(event) => setAnswer(event.target.value)}
          placeholder="Resposta ideal"
          className="min-h-28 w-full rounded-xl border border-white/15 bg-black/25 px-3 py-2 text-sm text-white outline-none transition focus:border-cyan/55"
        />
      </div>

      <div className="mt-4 flex justify-end">
        <button
          type="button"
          onClick={() => void handleAddFaq()}
          disabled={!question.trim() || !answer.trim() || busy}
          className="rounded-xl border border-cyan-300/40 bg-cyan/10 px-4 py-2 text-sm font-medium text-cyan-100 transition hover:bg-cyan/15 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {busy ? 'Salvando...' : 'Adicionar FAQ'}
        </button>
      </div>
    </section>
  );
}
