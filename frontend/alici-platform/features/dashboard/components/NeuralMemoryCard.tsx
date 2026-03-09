"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Brain } from "lucide-react";
import { api } from "@/services/api";

interface MemoryEntry {
  key: string;
  value: string;
  timestamp: string;
}

export function NeuralMemoryCard() {
  const [memories, setMemories] = useState<MemoryEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const res = await api.get<MemoryEntry[]>("/user/memory", { params: { limit: 5 } });
        if (active) setMemories(res.data ?? []);
      } catch {
        // Backend unavailable — show empty state
      } finally {
        if (active) setLoading(false);
      }
    }

    void load();
    return () => {
      active = false;
    };
  }, []);

  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Brain size={18} className="text-violet-400" />
          <h3 className="text-sm font-semibold text-slate-200">Memória Neural Persistente</h3>
        </div>
        <Link
          href="/memory"
          className="text-xs text-sky-400 transition hover:text-sky-300"
        >
          Gerenciar →
        </Link>
      </div>

      {loading ? (
        <p className="mt-4 text-xs text-slate-400">Carregando memórias...</p>
      ) : memories.length === 0 ? (
        <p className="mt-4 text-xs text-slate-400">
          Nenhuma memória semântica registrada ainda. Inicie uma conversa para que o sistema
          aprenda sobre você.
        </p>
      ) : (
        <ul className="mt-4 space-y-2">
          {memories.map((mem) => (
            <li
              key={mem.key}
              className="flex items-start justify-between rounded-lg bg-slate-800/60 px-3 py-2 text-xs"
            >
              <span className="font-medium text-violet-300">{mem.key}</span>
              <span className="ml-4 text-right text-slate-300">{mem.value}</span>
            </li>
          ))}
        </ul>
      )}

      <div className="mt-4 flex items-center gap-2">
        <span className="h-2 w-2 rounded-full bg-emerald-400" />
        <span className="text-xs text-slate-400">Sistema de memória ativo</span>
      </div>
    </section>
  );
}
