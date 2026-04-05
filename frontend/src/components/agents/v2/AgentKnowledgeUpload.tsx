import { useState } from 'react';

interface AgentKnowledgeUploadProps {
  onAdd: (payload: { title: string; kind: string; content: string }) => void;
}

export function AgentKnowledgeUpload({ onAdd }: AgentKnowledgeUploadProps) {
  const [title, setTitle] = useState('');
  const [kind, setKind] = useState('documento');
  const [content, setContent] = useState('');

  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <p className="font-semibold text-white">Adicionar material</p>
      <input value={title} onChange={(event) => setTitle(event.target.value)} placeholder="Titulo" className="mt-2 w-full rounded-xl border border-white/10 bg-black/25 px-3 py-2 text-sm text-white" />
      <input value={kind} onChange={(event) => setKind(event.target.value)} placeholder="Tipo" className="mt-2 w-full rounded-xl border border-white/10 bg-black/25 px-3 py-2 text-sm text-white" />
      <textarea value={content} onChange={(event) => setContent(event.target.value)} placeholder="Conteudo" className="mt-2 min-h-24 w-full rounded-xl border border-white/10 bg-black/25 px-3 py-2 text-sm text-white" />
      <button type="button" onClick={() => onAdd({ title, kind, content })} className="mt-2 rounded-xl bg-cyan px-3 py-2 text-sm font-semibold text-ink">Salvar material</button>
    </div>
  );
}
