import type { AccountPrivacy } from '../../types/account';

interface DataControlsPanelProps {
  privacy: AccountPrivacy | null;
  onExport: () => Promise<void>;
  onDeleteRequest: () => Promise<void>;
}

export function DataControlsPanel({ privacy, onExport, onDeleteRequest }: DataControlsPanelProps) {
  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
      <h2 className="font-display text-2xl text-white">Data Controls / Privacy</h2>
      <p className="mt-2 text-sm text-slate-300">Controle de dados, exportacao e solicitacao de exclusao de conta.</p>
      <ul className="mt-4 space-y-2 text-sm text-slate-100">
        {(privacy?.notes || []).map((note) => (
          <li key={note} className="rounded-2xl border border-white/10 bg-ink/40 px-3 py-2">{note}</li>
        ))}
      </ul>
      <div className="mt-4 flex flex-wrap gap-2">
        <button type="button" onClick={() => void onExport()} className="rounded-2xl border border-cyan/35 bg-cyan/10 px-4 py-2 text-sm text-cyan">
          Exportar meus dados
        </button>
        <button type="button" onClick={() => void onDeleteRequest()} className="rounded-2xl border border-white/20 px-4 py-2 text-sm text-slate-100">
          Solicitar exclusao da conta
        </button>
      </div>
    </section>
  );
}
