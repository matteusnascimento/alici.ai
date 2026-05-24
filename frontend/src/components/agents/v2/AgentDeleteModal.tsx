interface AgentDeleteModalProps {
  open: boolean;
  agentName: string;
  confirmText: string;
  deleting: boolean;
  error: string | null;
  onConfirmTextChange: (value: string) => void;
  onClose: () => void;
  onConfirm: () => void;
}

export function AgentDeleteModal({
  open,
  agentName,
  confirmText,
  deleting,
  error,
  onConfirmTextChange,
  onClose,
  onConfirm,
}: AgentDeleteModalProps) {
  if (!open) return null;

  const canConfirm = confirmText.trim() === agentName.trim() && !deleting;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/65 px-4">
      <div className="w-full max-w-xl rounded-3xl border border-rose-300/30 bg-[#0a1022] p-5">
        <p className="text-xs uppercase tracking-[0.18em] text-rose-200">Excluir agente</p>
        <h3 className="mt-2 font-display text-2xl text-white">Tem certeza que deseja excluir este agente?</h3>
        <p className="mt-2 text-sm text-slate-300">
          Essa acao removera configuracoes, testes, materiais e vinculos associados que nao puderem ser recuperados.
        </p>
        <p className="mt-3 text-sm text-slate-200">
          Digite o nome do agente para confirmar: <span className="font-semibold text-white">{agentName}</span>
        </p>

        <input
          value={confirmText}
          onChange={(event) => onConfirmTextChange(event.target.value)}
          placeholder={agentName}
          className="mt-3 w-full rounded-xl border border-white/15 bg-white/5 px-3 py-2 text-sm text-white placeholder:text-slate-500"
        />

        {error ? (
          <p className="mt-3 rounded-xl border border-rose-300/40 bg-rose-500/10 px-3 py-2 text-sm text-rose-100">
            {error}
          </p>
        ) : null}

        <div className="mt-4 flex flex-wrap justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            disabled={deleting}
            className="rounded-xl border border-white/20 px-4 py-2 text-sm text-slate-100 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={!canConfirm}
            className="rounded-xl border border-rose-300/50 bg-rose-500/15 px-4 py-2 text-sm font-semibold text-rose-100 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {deleting ? 'Excluindo...' : 'Excluir agente'}
          </button>
        </div>
      </div>
    </div>
  );
}
