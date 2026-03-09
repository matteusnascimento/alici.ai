"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { MessageSquare, ChevronRight } from "lucide-react";
import { DashboardLayout } from "@/layouts/DashboardLayout";
import { api } from "@/services/api";

interface ConversationSummary {
  id: string;
  title: string;
  last_message: string;
  last_message_at: string;
  message_count: number;
}

interface ApiEnvelope<T> {
  status: "success" | "error";
  data: T;
  error: string | null;
}

export default function HistoryPage() {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const res = await api.get<ApiEnvelope<{ conversations: ConversationSummary[] }>>(
          "/conversations",
          { params: { limit: 50 } }
        );
        if (active) setConversations(res.data?.data?.conversations ?? []);
      } catch {
        if (active) setConversations([]);
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
    <DashboardLayout>
      <section className="space-y-6">
        <header>
          <div className="flex items-center gap-3">
            <MessageSquare size={24} className="text-sky-400" />
            <div>
              <p className="text-xs uppercase tracking-widest text-slate-400">Conversas</p>
              <h1 className="text-2xl font-semibold">Histórico</h1>
            </div>
          </div>
          <p className="mt-2 text-sm text-slate-400">
            Todas as suas conversas com agentes de IA, ordenadas pela mais recente.
          </p>
        </header>

        <article className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
          {loading ? (
            <p className="text-sm text-slate-400">Carregando conversas...</p>
          ) : conversations.length === 0 ? (
            <div className="flex flex-col items-center gap-3 py-12 text-center">
              <MessageSquare size={40} className="text-slate-600" />
              <p className="text-sm text-slate-400">Nenhuma conversa encontrada.</p>
              <Link
                href="/chat"
                className="mt-2 rounded-lg bg-sky-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-sky-400"
              >
                Iniciar Chat
              </Link>
            </div>
          ) : (
            <ul className="divide-y divide-slate-800">
              {conversations.map((conv) => (
                <li key={conv.id}>
                  <Link
                    href={`/chat/${conv.id}`}
                    className="flex items-center justify-between py-4 transition hover:text-sky-300"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-slate-100">
                        {conv.title || "Conversa sem título"}
                      </p>
                      {conv.last_message && (
                        <p className="mt-0.5 truncate text-xs text-slate-400">
                          {conv.last_message}
                        </p>
                      )}
                    </div>
                    <div className="ml-4 flex shrink-0 items-center gap-3">
                      {conv.message_count > 0 && (
                        <span className="text-xs text-slate-500">
                          {conv.message_count} msg
                        </span>
                      )}
                      {conv.last_message_at && (
                        <span className="text-xs text-slate-500">
                          {new Date(conv.last_message_at).toLocaleDateString("pt-BR")}
                        </span>
                      )}
                      <ChevronRight size={16} className="text-slate-600" />
                    </div>
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </article>
      </section>
    </DashboardLayout>
  );
}
