import { UploadCloud, X } from 'lucide-react';
import { useMemo, useRef, useState } from 'react';

interface AgentKnowledgeUploadProps {
  busy?: boolean;
  onUploadFiles: (files: File[]) => Promise<void>;
}

const ACCEPTED_TYPES = '.pdf,.docx,.txt,.csv,.json';

function formatBytes(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  const kb = bytes / 1024;
  if (kb < 1024) return `${kb.toFixed(1)} KB`;
  return `${(kb / 1024).toFixed(1)} MB`;
}

export function AgentKnowledgeUpload({ busy = false, onUploadFiles }: AgentKnowledgeUploadProps) {
  const [queuedFiles, setQueuedFiles] = useState<File[]>([]);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const hasFiles = queuedFiles.length > 0;
  const totalSize = useMemo(
    () => queuedFiles.reduce((total, file) => total + file.size, 0),
    [queuedFiles],
  );

  function appendFiles(files: FileList | null) {
    if (!files) return;
    const next = Array.from(files).filter((file) => file.name);
    if (next.length === 0) return;
    setQueuedFiles((current) => {
      const seen = new Set(current.map((item) => `${item.name}:${item.size}`));
      const merged = [...current];
      for (const file of next) {
        const key = `${file.name}:${file.size}`;
        if (!seen.has(key)) {
          seen.add(key);
          merged.push(file);
        }
      }
      return merged;
    });
  }

  async function handleUpload() {
    if (!hasFiles || busy) return;
    await onUploadFiles(queuedFiles);
    setQueuedFiles([]);
  }

  return (
    <section className="rounded-3xl border border-white/10 bg-gradient-to-b from-white/[0.09] to-white/[0.03] p-5 shadow-soft">
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <h2 className="font-display text-lg text-white">Upload de arquivos</h2>
          <p className="mt-1 text-sm text-slate-300">Envie materiais para treino do agente. Formatos: PDF, DOCX, TXT, CSV e JSON.</p>
        </div>
        <span className="rounded-full border border-cyan/35 bg-cyan/10 px-3 py-1 text-xs font-medium text-cyan-100">Knowledge Files</span>
      </div>

      <div
        role="presentation"
        onDragOver={(event) => {
          event.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(event) => {
          event.preventDefault();
          setDragging(false);
          appendFiles(event.dataTransfer?.files ?? null);
        }}
        className={[
          'flex min-h-40 flex-col items-center justify-center rounded-2xl border border-dashed px-4 py-6 text-center transition',
          dragging ? 'border-cyan bg-cyan/10' : 'border-white/25 bg-ink/40',
        ].join(' ')}
      >
        <UploadCloud className="h-8 w-8 text-cyan" />
        <p className="mt-3 text-sm font-medium text-white">Arraste arquivos aqui ou selecione do computador</p>
        <p className="mt-1 text-xs text-slate-400">Limite recomendado de 10MB por arquivo</p>
        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className="mt-4 rounded-xl border border-white/20 bg-white/5 px-4 py-2 text-sm font-medium text-slate-100 transition hover:border-cyan/50 hover:text-white"
        >
          Selecionar arquivos
        </button>
        <input
          ref={inputRef}
          type="file"
          multiple
          accept={ACCEPTED_TYPES}
          className="hidden"
          onChange={(event) => {
            appendFiles(event.target.files);
            event.currentTarget.value = '';
          }}
        />
      </div>

      <div className="mt-4 rounded-2xl border border-white/10 bg-black/20 p-3">
        <div className="mb-2 flex items-center justify-between">
          <p className="text-sm font-medium text-slate-100">Fila de upload</p>
          <p className="text-xs text-slate-400">{hasFiles ? `${queuedFiles.length} arquivo(s) • ${formatBytes(totalSize)}` : 'Nenhum arquivo selecionado'}</p>
        </div>
        <div className="max-h-40 space-y-2 overflow-auto pr-1">
          {queuedFiles.map((file) => (
            <div key={`${file.name}-${file.size}`} className="flex items-center justify-between rounded-xl border border-white/10 bg-white/[0.03] px-3 py-2">
              <div className="min-w-0">
                <p className="truncate text-sm text-white">{file.name}</p>
                <p className="text-xs text-slate-400">{formatBytes(file.size)}</p>
              </div>
              <button
                type="button"
                onClick={() => setQueuedFiles((current) => current.filter((item) => !(item.name === file.name && item.size === file.size)))}
                className="inline-flex h-7 w-7 items-center justify-center rounded-lg border border-white/15 text-slate-300 transition hover:border-rose-300/50 hover:text-rose-200"
                aria-label={`Remover ${file.name}`}
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-4 flex justify-end">
        <button
          type="button"
          onClick={() => void handleUpload()}
          disabled={!hasFiles || busy}
          className="rounded-xl bg-cyan px-4 py-2 text-sm font-semibold text-ink transition hover:bg-cyan-300 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {busy ? 'Enviando...' : 'Enviar materiais'}
        </button>
      </div>
    </section>
  );
}
