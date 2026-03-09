"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "@/services/api";

interface KnowledgeDocument {
  id: string;
  filename: string;
  created_at: string;
  status?: string;
}

export default function KnowledgeRoute() {
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [isError, setIsError] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [loadingDocs, setLoadingDocs] = useState(true);
  const fileInputRef = useRef<HTMLInputElement>(null);

  async function loadDocuments() {
    try {
      const res = await api.get<{ data: { documents: KnowledgeDocument[] } }>("/knowledge");
      const data = res.data?.data ?? res.data;
      setDocuments(data?.documents ?? []);
    } catch {
      // ignore – listing may not be available
    } finally {
      setLoadingDocs(false);
    }
  }

  useEffect(() => {
    void loadDocuments();
  }, []);

  const uploadingRef = useRef(false);

  async function uploadFile(file: File) {
    if (uploadingRef.current) return;
    const form = new FormData();
    form.append("file", file);

    uploadingRef.current = true;
    setUploading(true);
    setMessage(null);
    setIsError(false);
    try {
      await api.post("/knowledge/upload", form);
      setMessage(`"${file.name}" uploaded successfully.`);
      void loadDocuments();
    } catch {
      setIsError(true);
      setMessage("Upload failed. Verify authentication and try again.");
    } finally {
      uploadingRef.current = false;
      setUploading(false);
    }
  }

  function handleFileInput(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (file) void uploadFile(file);
    event.target.value = "";
  }

  const handleDrop = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      setIsDragOver(false);
      const file = event.dataTransfer.files?.[0];
      if (file) void uploadFile(file);
    },
    // uploadFile is defined in the same component scope and stable via uploadingRef
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  function handleDragOver(event: React.DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragOver(true);
  }

  function handleDragLeave() {
    setIsDragOver(false);
  }

  return (
      <section className="space-y-6">
        <header>
          <p className="text-xs uppercase tracking-widest text-slate-400">Neural Memory</p>
          <h1 className="text-2xl font-semibold">Knowledge Base</h1>
          <p className="mt-1 text-sm text-slate-400">
            Upload PDFs and documents to index them for RAG — your agents will use this knowledge
            to answer questions accurately.
          </p>
        </header>

        {/* Drag-and-drop upload area */}
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => !uploading && fileInputRef.current?.click()}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") fileInputRef.current?.click();
          }}
          className={`flex cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed p-10 text-center transition ${
            isDragOver
              ? "border-sky-400 bg-sky-500/10"
              : uploading
              ? "cursor-not-allowed border-slate-700 bg-slate-900/40 opacity-60"
              : "border-slate-700 bg-slate-900/40 hover:border-sky-500/50 hover:bg-sky-500/5"
          }`}
        >
          <span className="text-4xl">📂</span>
          <div>
            <p className="font-medium text-slate-200">
              {uploading ? "Uploading..." : isDragOver ? "Drop file here" : "Drag & drop a file here"}
            </p>
            <p className="mt-1 text-sm text-slate-400">
              or <span className="text-sky-400 underline">click to browse</span> — PDF, DOCX, TXT, MD, CSV supported
            </p>
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.txt,.md,.csv"
            className="hidden"
            onChange={handleFileInput}
            disabled={uploading}
          />
        </div>

        {message && (
          <p className={`text-sm ${isError ? "text-red-400" : "text-emerald-400"}`}>{message}</p>
        )}

        {/* Document list */}
        <div>
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-widest text-slate-400">
            Indexed Documents
          </h2>
          {loadingDocs ? (
            <p className="text-sm text-slate-400">Loading documents...</p>
          ) : documents.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/40 p-6 text-center">
              <p className="text-sm text-slate-400">
                No documents indexed yet. Upload your first file above.
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-900/70 px-4 py-3"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-lg">📄</span>
                    <span className="text-sm text-slate-100">{doc.filename}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    {doc.status && (
                      <span className="text-xs text-emerald-400">{doc.status}</span>
                    )}
                    <span className="text-xs text-slate-400">{doc.created_at}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
  );
}
