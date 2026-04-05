interface StudioExportModalProps {
  open: boolean;
  onClose: () => void;
  onExport: (format: 'png' | 'jpg' | 'webp' | 'mp4' | 'pdf' | 'zip') => void;
}

const formats: Array<'png' | 'jpg' | 'webp' | 'mp4' | 'pdf' | 'zip'> = ['png', 'jpg', 'webp', 'mp4', 'pdf', 'zip'];

export function StudioExportModal({ open, onClose, onExport }: StudioExportModalProps) {
  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/60 px-4">
      <div className="w-full max-w-md rounded-3xl border border-cyan-300/30 bg-[linear-gradient(160deg,#061022,#0f2647)] p-5">
        <h3 className="font-display text-2xl text-white">Exportar projeto</h3>
        <p className="mt-2 text-sm text-slate-300">Selecione um formato de saida profissional.</p>
        <div className="mt-4 grid grid-cols-3 gap-2">
          {formats.map((format) => (
            <button key={format} type="button" onClick={() => onExport(format)} className="rounded-xl border border-white/15 bg-white/5 px-3 py-2 text-sm font-semibold uppercase text-slate-100 hover:border-cyan-300/40 hover:text-cyan-100">
              {format}
            </button>
          ))}
        </div>
        <button type="button" onClick={onClose} className="mt-4 w-full rounded-xl border border-white/15 px-3 py-2 text-sm text-slate-200 hover:text-white">
          Fechar
        </button>
      </div>
    </div>
  );
}
