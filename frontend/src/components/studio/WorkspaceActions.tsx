interface WorkspaceActionsProps {
  onGenerate: () => void;
  onRegenerate: () => void;
  onSave: () => void;
  onDuplicate?: () => void;
  onExport?: () => void;
  onReset: () => void;
  loading: boolean;
}

export function WorkspaceActions({
  onGenerate,
  onRegenerate,
  onSave,
  onDuplicate,
  onExport,
  onReset,
  loading,
}: WorkspaceActionsProps) {
  return (
    <div className="flex flex-wrap gap-2">
      <button type="button" onClick={onGenerate} disabled={loading} className="rounded-2xl bg-sand px-4 py-2 text-sm font-semibold text-ink">
        {loading ? 'Processando...' : 'Gerar'}
      </button>
      <button type="button" onClick={onRegenerate} className="rounded-2xl border border-white/20 px-4 py-2 text-sm text-slate-100">
        Regenerar
      </button>
      <button type="button" onClick={onSave} className="rounded-2xl border border-cyan/35 bg-cyan/10 px-4 py-2 text-sm text-cyan">
        Salvar projeto
      </button>
      {onDuplicate ? (
        <button type="button" onClick={onDuplicate} className="rounded-2xl border border-white/20 px-4 py-2 text-sm text-slate-100">
          Duplicar
        </button>
      ) : null}
      {onExport ? (
        <button type="button" onClick={onExport} className="rounded-2xl border border-white/20 px-4 py-2 text-sm text-slate-100">
          Exportar
        </button>
      ) : null}
      <button type="button" onClick={onReset} className="rounded-2xl border border-white/20 px-4 py-2 text-sm text-slate-100">
        Limpar
      </button>
    </div>
  );
}
