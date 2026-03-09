"use client";

import { useRef, useState } from "react";
import { getAccessToken } from "@/services/authSession";

interface Message { id: string; role: "user" | "assistant"; content: string }

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

export function DashboardChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  function scrollBottom() {
    setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
  }

  async function handleSend() {
    const text = draft.trim();
    if (!text || sending) return;

    const userId = `u-${Date.now()}`;
    const assistantId = `a-${Date.now()}`;

    setMessages((prev: Message[]) => [
      ...prev,
      { id: userId, role: "user", content: text },
      { id: assistantId, role: "assistant", content: "" },
    ]);
    setDraft("");
    setSending(true);
    setError(null);
    scrollBottom();

    try {
      const token = getAccessToken();
      const response = await fetch(`${API_BASE}/chat/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({ message: text }),
      });

      if (!response.ok || !response.body) throw new Error("Stream failed");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split("\n\n");
        buffer = events.pop() ?? "";

        for (const event of events) {
          const line = event.split("\n").find((l: string) => l.startsWith("data:"));
          if (!line) continue;
          const payload = line.slice(5).trim();
          if (payload === "[DONE]") break;
          try {
            const parsed = JSON.parse(payload) as { data?: { chunk?: string } };
            const chunk = parsed?.data?.chunk ?? "";
            if (chunk) {
              setMessages((prev: Message[]) =>
                prev.map((m: Message) => m.id === assistantId ? { ...m, content: m.content + chunk } : m)
              );
              scrollBottom();
            }
          } catch { /* ignore malformed chunk */ }
        }
      }
      reader.releaseLock();
    } catch {
      setMessages((prev: Message[]) =>
        prev.map((m: Message) =>
          m.id === assistantId && !m.content
            ? { ...m, content: "Erro ao conectar com o servidor. Verifique a autenticação." }
            : m
        )
      );
      setError("Falha ao enviar mensagem.");
    } finally {
      setSending(false);
      scrollBottom();
    }
  }

  function handleClear() {
    setMessages([]);
    setError(null);
  }

  return (
    <div className="flex min-h-[520px] flex-col rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-800 px-4 py-3">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-emerald-400" />
          <span className="text-sm font-semibold text-slate-200">AI Chat</span>
          <span className="rounded-full border border-slate-700 px-2 py-0.5 text-xs text-slate-400">
            /api/chat/stream
          </span>
        </div>
        {messages.length > 0 && (
          <button type="button" onClick={handleClear}
            className="text-xs text-slate-500 hover:text-slate-300 transition">
            Limpar conversa
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-3 px-4 py-4">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center gap-3 py-12 text-center">
            <div className="rounded-full border border-slate-700 bg-slate-800 p-4 text-3xl">💬</div>
            <p className="text-sm font-medium text-slate-300">Inicie uma conversa com a IA</p>
            <div className="flex flex-wrap justify-center gap-2 mt-2">
              {["O que é RAG?", "Crie um agente de suporte", "Explique embeddings"].map((s) => (
                <button key={s} type="button"
                  onClick={() => { setDraft(s); }}
                  className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs text-slate-300 hover:border-sky-500 hover:bg-sky-500/10 transition">
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((m) => (
            <article key={m.id}
              className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
              {m.role === "assistant" && (
                <div className="mr-2 mt-1 h-7 w-7 shrink-0 rounded-full bg-sky-500/20 flex items-center justify-center text-sm">
                  🤖
                </div>
              )}
              <div className={`max-w-[75%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                m.role === "user"
                  ? "bg-sky-500 text-white rounded-br-sm"
                  : "bg-slate-800 text-slate-100 rounded-bl-sm"
              }`}>
                {m.content || <span className="animate-pulse text-slate-400">●●●</span>}
              </div>
              {m.role === "user" && (
                <div className="ml-2 mt-1 h-7 w-7 shrink-0 rounded-full bg-slate-700 flex items-center justify-center text-sm">
                  👤
                </div>
              )}
            </article>
          ))
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t border-slate-800 p-3">
        {error && <p className="mb-2 text-xs text-red-400">{error}</p>}
        <div className="flex items-end gap-2">
          <textarea
            value={draft}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setDraft(e.target.value)}
            onKeyDown={(e: React.KeyboardEvent<HTMLTextAreaElement>) => {
              if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); void handleSend(); }
            }}
            placeholder="Digite sua mensagem... (Enter para enviar, Shift+Enter para nova linha)"
            rows={2}
            className="flex-1 resize-none rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
          />
          <button type="button" onClick={() => void handleSend()}
            disabled={sending || !draft.trim()}
            className="rounded-xl bg-sky-500 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-sky-400 disabled:opacity-50">
            {sending ? "..." : "Enviar"}
          </button>
        </div>
      </div>
    </div>
  );
}
