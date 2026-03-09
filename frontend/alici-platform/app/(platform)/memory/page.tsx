"use client";

import { useEffect, useState } from "react";
import { Brain, Trash2 } from "lucide-react";
import { api } from "@/services/api";

interface MemoryEntry {
  key: string;
  value: string;
  timestamp: string;
}

export default function MemoryPage() {
  const [memories, setMemories] = useState<MemoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [newKey, setNewKey] = useState("");
  const [newValue, setNewValue] = useState("");
  const [saving, setSaving] = useState(false);

  const [deleting, setDeleting] = useState<string | null>(null);

  async function loadMemories() {
    setLoading(true);
    try {
      const res = await api.get<MemoryEntry[]>("/user/memory", { params: { limit: 100 } });
      setMemories(res.data ?? []);
    } catch {
      setMemories([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadMemories();
  }, []);

  async function handleDelete(key: string) {
    setDeleting(key);
    try {
      await api.delete(`/user/memory/${encodeURIComponent(key)}`);
      setMemories((prev) => prev.filter((m) => m.key !== key));
    } catch {
      // ignore
    } finally {
      setDeleting(null);
    }
  }

  async function handleAdd(e: React.FormEvent) {
    e.preventDefault();
    if (!newKey.trim() || !newValue.trim()) return;
    setSaving(true);
    try {
      await api.put("/user/memory", { key: newKey.trim(), value: newValue.trim() });
      setNewKey("");
      setNewValue("");
      await loadMemories();
    } catch {
      // ignore
    } finally {
      setSaving(false);
    }
  }

  return (
      <section className="space-y-6">
        <header>
          <div className="flex items-center gap-3">
            <Brain size={24} className="text-violet-400" />
            <div>
              <p className="text-xs uppercase tracking-widest text-slate-400">IA</p>
              <h1 className="text-2xl font-semibold">Memória Neural Persistente</h1>
            </div>
          </div>
          <p className="mt-2 max-w-2xl text-sm text-slate-400">
            O sistema extrai e armazena automaticamente fatos semânticos das suas conversas.
            Você pode visualizar, adicionar ou gerenciar esses dados contextuais abaixo.
          </p>
        </header>

        <article className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
          <h2 className="mb-4 text-sm font-semibold text-slate-200">Adicionar Memória</h2>
          <form onSubmit={(e) => void handleAdd(e)} className="flex flex-wrap gap-3">
            <input
              type="text"
              placeholder="Chave (ex: user_name)"
              value={newKey}
              onChange={(e) => setNewKey(e.target.value)}
              className="flex-1 min-w-[160px] rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 outline-none focus:border-sky-500"
            />
            <input
              type="text"
              placeholder="Valor (ex: João)"
              value={newValue}
              onChange={(e) => setNewValue(e.target.value)}
              className="flex-1 min-w-[160px] rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 outline-none focus:border-sky-500"
            />
            <button
              type="submit"
              disabled={saving}
              className="rounded-lg bg-sky-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-sky-400 disabled:opacity-60"
            >
              {saving ? "Salvando..." : "Salvar"}
            </button>
          </form>
        </article>

        <article className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-slate-200">Memórias Armazenadas</h2>
            <div className="flex items-center gap-2">
              <span className="h-2 w-2 rounded-full bg-emerald-400" />
              <span className="text-xs text-slate-400">Sistema ativo</span>
            </div>
          </div>

          {loading ? (
            <p className="mt-4 text-sm text-slate-400">Carregando memórias...</p>
          ) : memories.length === 0 ? (
            <div className="mt-6 flex flex-col items-center gap-3 py-8 text-center">
              <Brain size={40} className="text-slate-600" />
              <p className="text-sm text-slate-400">
                Nenhuma memória semântica registrada ainda.
              </p>
              <p className="text-xs text-slate-500">
                O sistema aprende automaticamente durante as suas conversas no Chat.
              </p>
            </div>
          ) : (
            <ul className="mt-4 divide-y divide-slate-800">
              {memories.map((mem) => (
                <li key={mem.key} className="flex items-center justify-between py-3">
                  <div>
                    <span className="text-xs font-semibold uppercase tracking-wide text-violet-400">
                      {mem.key}
                    </span>
                    <p className="mt-0.5 text-sm text-slate-200">{mem.value}</p>
                    {mem.timestamp && (
                      <p className="mt-0.5 text-xs text-slate-500">
                        {new Date(mem.timestamp).toLocaleString("pt-BR")}
                      </p>
                    )}
                  </div>
                  <button
                    type="button"
                    aria-label={`Remover memória ${mem.key}`}
                    onClick={() => void handleDelete(mem.key)}
                    disabled={deleting === mem.key}
                    className="ml-4 rounded-lg p-2 text-slate-500 transition hover:bg-slate-800 hover:text-red-400 disabled:opacity-50"
                  >
                    <Trash2 size={16} />
                  </button>
                </li>
              ))}
            </ul>
          )}
        </article>
      </section>
  );
}
