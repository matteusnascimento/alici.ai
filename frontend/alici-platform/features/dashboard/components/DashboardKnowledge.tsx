"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "@/services/api";

interface Doc { id: string; filename: string; total_chunks: number; created_at: string; status?: string }

const PIPELINE = ["Upload", "Parse", "Chunk", "Embed", "Store", "Retrieve"];

export function DashboardKnowledge() {
  const [docs, setDocs] = useState<Doc[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [message, setMessage] = useState<{ text: string; ok: boolean } | null>(null);
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [querying, setQuerying] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const uploadingRef = useRef(false);

  async function loadDocs() {
    try {
      const res = await api.get<{ data: { documents: Doc[] } }>("/knowledge/list");
      const data = res.data?.data ?? (res.data as unknown as { documents: Doc[] });
      setDocs(data?.documents ?? []);
    } catch { /* ignore */ } finally { setLoading(false); }
  }

  useEffect(() => { void loadDocs(); }, []);

  async function uploadFile(file: File) {
    if (uploadingRef.current) return;
    uploadingRef.current = true;
    setUploading(true);
    setMessage(null);
    const form = new FormData();
    form.append("file", file);
    try {
      await api.post("/knowledge/upload", form);
      setMessage({ text: `"${file.name}" indexado com sucesso.`, ok: true });
      void loadDocs();
    } catch {
      setMessage({ text: "Upload falhou. Verifique a autenticação.", ok: false });
    } finally {
      uploadingRef.current = false;
      setUploading(false);
    }
  }

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) void uploadFile(file);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleQuery(e: React.FormEvent) {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;
    setQuerying(true);
    setAnswer(null);
    try {
      const res = await api.post<{ data: { answer: string } }>("/knowledge/query", { query: q, top_k: 5 });
      setAnswer(res.data?.data?.answer ?? "Sem resposta.");
    } catch { setAnswer("Erro ao consultar a base de conhecimento."); }
    finally { setQuerying(false); }
  }

  async function handleDelete(id: string) {
    try {
      await api.delete(`/knowledge/${id}`);
      setDocs((prev) => prev.filter((d) => d.id !== id));
    } catch { /* ignore */ }
  }

  return (
    <div className="space-y-6">
      {/* RAG Pipeline banner */}
      <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4">
        <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-slate-400">Pipeline RAG</p>
        <div className="flex flex-wrap items-center gap-2">
          {PIPELINE.map((step, i) => (
            <span key={step} className="flex items-center gap-2">
              <span className="rounded-lg border border-sky-500/30 bg-sky-500/10 px-3 py-1 text-xs font-medium text-sky-300">
                {step}
              </span>
              {i < PIPELINE.length - 1 && <span className="text-slate-600">→</span>}
            </span>
          ))}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Upload area */}
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-slate-200">Upload de Documentos</h3>
          <div
            onDrop={handleDrop}
            onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
            onDragLeave={() => setIsDragOver(false)}
            onClick={() => !uploading && fileRef.current?.click()}
            role="button" tabIndex={0}
            onKeyDown={(e) => { if (e.key === "Enter") fileRef.current?.click(); }}
            className={`flex cursor-pointer flex-col items-center gap-3 rounded-xl border-2 border-dashed p-8 text-center transition ${
              isDragOver ? "border-sky-400 bg-sky-500/10"
              : uploading ? "cursor-not-allowed border-slate-700 opacity-60"
              : "border-slate-700 hover:border-sky-500/50 hover:bg-sky-500/5"
            }`}
          >
            <span className="text-3xl">📂</span>
            <div>
              <p className="text-sm font-medium text-slate-200">
                {uploading ? "Enviando..." : isDragOver ? "Solte aqui" : "Arraste ou clique para enviar"}
              </p>
              <p className="mt-1 text-xs text-slate-500">PDF · DOCX · TXT · CSV</p>
            </div>
            <input ref={fileRef} type="file" accept=".pdf,.docx,.txt,.csv"
              className="hidden" disabled={uploading}
              onChange={(e) => { const f = e.target.files?.[0]; if (f) void uploadFile(f); e.target.value = ""; }} />
          </div>
          {message && (
            <p className={`text-sm ${message.ok ? "text-emerald-400" : "text-red-400"}`}>{message.text}</p>
          )}
        </div>

        {/* RAG Query */}
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-slate-200">Consultar Base de Conhecimento</h3>
          <form onSubmit={(e: React.FormEvent) => void handleQuery(e)} className="space-y-2">
            <textarea value={query} onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setQuery(e.target.value)}
              rows={3} placeholder="Faça uma pergunta sobre seus documentos..."
              className="w-full resize-none rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500" />
            <button type="submit" disabled={querying || !query.trim()}
              className="w-full rounded-lg bg-sky-500 py-2 text-sm font-semibold text-white disabled:opacity-50">
              {querying ? "Consultando..." : "🔍 Consultar RAG"}
            </button>
          </form>
          {answer && (
            <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-4">
              <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-2">Resposta</p>
              <p className="text-sm text-slate-200 whitespace-pre-wrap">{answer}</p>
            </div>
          )}
        </div>
      </div>

      {/* Document list */}
      <div>
        <h3 className="mb-3 text-sm font-semibold uppercase tracking-widest text-slate-400">
          Documentos Indexados {docs.length > 0 && `(${docs.length})`}
        </h3>
        {loading ? (
          <p className="text-sm text-slate-400">Carregando documentos...</p>
        ) : docs.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-700 bg-slate-900/40 p-6 text-center">
            <p className="text-sm text-slate-500">Nenhum documento indexado ainda.</p>
          </div>
        ) : (
          <div className="space-y-2">
            {docs.map((doc) => (
              <div key={doc.id}
                className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-900/70 px-4 py-3">
                <div className="flex items-center gap-3">
                  <span className="text-lg">📄</span>
                  <div>
                    <p className="text-sm text-slate-100">{doc.filename}</p>
                    <p className="text-xs text-slate-500">{doc.total_chunks} chunks · {new Date(doc.created_at).toLocaleDateString("pt-BR")}</p>
                  </div>
                </div>
                <button type="button" onClick={() => void handleDelete(doc.id)}
                  className="rounded-lg px-2 py-1 text-xs text-red-400 hover:bg-red-500/10 transition">
                  Remover
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
