import { useState } from 'react';

interface AgentActionConfigModalProps {
  open: boolean;
  actionName: string;
  onClose: () => void;
  onSave: (config: Record<string, unknown>) => void;
}

export function AgentActionConfigModal({ open, actionName, onClose, onSave }: AgentActionConfigModalProps) {
  const [jsonText, setJsonText] = useState('{}');

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/60 px-4">
      <div className="w-full max-w-md rounded-3xl border border-cyan-300/30 bg-[linear-gradient(160deg,#061022,#0f2647)] p-5">
        <h3 className="font-display text-xl text-white">Configurar acao: {actionName}</h3>
        <textarea value={jsonText} onChange={(event) => setJsonText(event.target.value)} className="mt-3 min-h-28 w-full rounded-xl border border-white/10 bg-black/25 px-3 py-2 text-sm text-white" />
        <div className="mt-3 flex gap-2">
          <button type="button" onClick={() => { try { onSave(JSON.parse(jsonText)); onClose(); } catch { } }} className="rounded-xl bg-cyan px-4 py-2 text-sm font-semibold text-ink">Salvar</button>
          <button type="button" onClick={onClose} className="rounded-xl border border-white/20 px-4 py-2 text-sm text-slate-100">Fechar</button>
        </div>
      </div>
    </div>
  );
}
