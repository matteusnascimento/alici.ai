import { useState } from 'react';

interface ProductPhotoWorkspaceProps {
  onNotify: (msg: string) => void;
}

const styleOptions = ['ecommerce', 'premium', 'social', 'catalog'];

export function ProductPhotoWorkspace({ onNotify }: ProductPhotoWorkspaceProps) {
  const [style, setStyle] = useState('premium');
  const [prompt, setPrompt] = useState('fundo elegante, luz suave, destaque no produto');
  const [uploaded, setUploaded] = useState<string>('');

  return (
    <div className="grid gap-6 xl:grid-cols-[360px_1fr]">
      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
        <h3 className="font-display text-2xl text-white">Fotos do Produto</h3>
        <p className="mt-2 text-sm text-slate-300">Upload, prompt criativo e estilo de renderizacao.</p>

        <label className="mt-4 block rounded-2xl border border-dashed border-white/20 bg-ink/40 p-6 text-center text-sm text-slate-300">
          <input
            type="file"
            className="hidden"
            onChange={(event) => {
              const file = event.target.files?.[0];
              setUploaded(file?.name || '');
              if (file) onNotify(`Arquivo selecionado: ${file.name}`);
            }}
          />
          Clique para enviar imagem base
        </label>
        {uploaded ? <p className="mt-2 text-xs text-cyan">Arquivo: {uploaded}</p> : null}

        <label className="mt-4 block space-y-2 text-sm text-slate-300">
          <span>Prompt visual</span>
          <textarea
            className="h-28 w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white outline-none focus:border-cyan"
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
          />
        </label>

        <div className="mt-4 grid grid-cols-2 gap-2">
          {styleOptions.map((item) => (
            <button
              key={item}
              type="button"
              onClick={() => setStyle(item)}
              className={[
                'rounded-xl border px-3 py-2 text-sm capitalize transition',
                style === item ? 'border-cyan/40 bg-cyan/10 text-cyan' : 'border-white/15 text-slate-200',
              ].join(' ')}
            >
              {item}
            </button>
          ))}
        </div>
      </section>

      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
        <h3 className="font-display text-2xl text-white">Preview de resultados</h3>
        <p className="mt-2 text-sm text-slate-300">Simulacao de saidas para estilo {style}.</p>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((slot) => (
            <div key={slot} className="aspect-square rounded-2xl border border-white/10 bg-gradient-to-br from-storm/60 to-ink/70 p-3">
              <p className="text-xs text-slate-300">Preview {slot}</p>
              <p className="mt-2 text-sm text-slate-100">{prompt.slice(0, 46)}...</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
