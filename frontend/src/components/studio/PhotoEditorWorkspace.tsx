import { useState } from 'react';

interface PhotoEditorWorkspaceProps {
  onNotify: (msg: string) => void;
}

const actions = ['remover fundo', 'aprimorar', 'recortar', 'redimensionar', 'ajustar luz', 'limpar imagem'];

export function PhotoEditorWorkspace({ onNotify }: PhotoEditorWorkspaceProps) {
  const [activeAction, setActiveAction] = useState(actions[0]);

  return (
    <div className="grid gap-6 xl:grid-cols-[250px_1fr]">
      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-4">
        <h3 className="font-display text-xl text-white">Editor de Fotos IA</h3>
        <div className="mt-4 space-y-2">
          {actions.map((action) => (
            <button
              key={action}
              type="button"
              onClick={() => {
                setActiveAction(action);
                onNotify(`Acao selecionada: ${action}.`);
              }}
              className={[
                'w-full rounded-xl border px-3 py-2 text-left text-sm capitalize transition',
                action === activeAction ? 'border-cyan/40 bg-cyan/10 text-cyan' : 'border-white/10 text-slate-200',
              ].join(' ')}
            >
              {action}
            </button>
          ))}
        </div>
      </section>

      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
        <label className="mb-4 flex h-36 items-center justify-center rounded-2xl border border-dashed border-white/20 bg-ink/40 text-sm text-slate-300">
          <input type="file" className="hidden" />
          Clique para enviar imagem
        </label>

        <div className="grid gap-4 xl:grid-cols-2">
          <div className="min-h-[340px] rounded-2xl border border-white/10 bg-gradient-to-br from-storm/70 to-ink/70 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-300">Preview original</p>
          </div>
          <div className="min-h-[340px] rounded-2xl border border-cyan/30 bg-gradient-to-br from-cyan/10 to-ink/70 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-cyan">Preview editado: {activeAction}</p>
          </div>
        </div>
      </section>
    </div>
  );
}
