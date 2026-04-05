import { useState } from 'react';

interface AgentFaqManagerProps {
  onAddFaq: (question: string, answer: string) => void;
}

export function AgentFaqManager({ onAddFaq }: AgentFaqManagerProps) {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <p className="font-semibold text-white">Perguntas frequentes</p>
      <input value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Pergunta" className="mt-2 w-full rounded-xl border border-white/10 bg-black/25 px-3 py-2 text-sm text-white" />
      <textarea value={answer} onChange={(event) => setAnswer(event.target.value)} placeholder="Resposta" className="mt-2 min-h-20 w-full rounded-xl border border-white/10 bg-black/25 px-3 py-2 text-sm text-white" />
      <button type="button" onClick={() => onAddFaq(question, answer)} className="mt-2 rounded-xl border border-cyan-300/40 px-3 py-2 text-sm text-cyan-100">Adicionar FAQ</button>
    </div>
  );
}
