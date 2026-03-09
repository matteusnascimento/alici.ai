"use client";

import { useState } from "react";
import { DashboardLayout } from "@/layouts/DashboardLayout";
import { api } from "@/services/api";

export default function KnowledgeRoute() {
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function uploadFile(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    const form = new FormData();
    form.append("file", file);

    setUploading(true);
    setMessage(null);
    try {
      await api.post("/knowledge/upload", form);
      setMessage("Upload concluido com sucesso.");
    } catch {
      setMessage("Falha no upload. Verifique autenticacao e tente novamente.");
    } finally {
      setUploading(false);
      event.target.value = "";
    }
  }

  return (
    <DashboardLayout>
      <main className="space-y-4 p-2">
        <h1 className="text-2xl font-semibold">Knowledge Base</h1>
        <p className="text-sm text-slate-300">Envie documentos para indexacao e uso no RAG.</p>

        <label className="inline-flex cursor-pointer items-center gap-3 rounded-lg border border-slate-700 bg-slate-900 px-4 py-3 text-sm">
          <span>{uploading ? "Enviando..." : "Selecionar arquivo"}</span>
          <input type="file" className="hidden" onChange={uploadFile} disabled={uploading} />
        </label>

        {message ? <p className="text-sm text-slate-300">{message}</p> : null}
      </main>
    </DashboardLayout>
  );
}
