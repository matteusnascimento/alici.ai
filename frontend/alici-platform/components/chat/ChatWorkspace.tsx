"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  ChatMessage,
  ConversationItem,
  createConversation,
  getConversationMessages,
  getConversations,
  streamMessage
} from "@/services/chatService";
import { fetchAgents } from "@/features/agents/services/agentService";
import type { AgentItem } from "@/features/agents/types/agentTypes";

interface ChatWorkspaceProps {
  initialConversationId?: string;
}

export function ChatWorkspace({ initialConversationId }: ChatWorkspaceProps) {
  const router = useRouter();
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(
    initialConversationId ?? null
  );
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [agents, setAgents] = useState<AgentItem[]>([]);
  const [selectedAgentId, setSelectedAgentId] = useState<string>("");
  const agentLoadedRef = useRef(false);

  // Load available agents for the selector once on mount
  useEffect(() => {
    if (agentLoadedRef.current) return;
    agentLoadedRef.current = true;

    async function loadAgents() {
      try {
        const data = await fetchAgents();
        setAgents(data.agents);
        if (data.agents.length > 0) {
          setSelectedAgentId((prev) => prev || data.agents[0].id);
        }
      } catch {
        // Ignore – agent selector is optional
      }
    }

    void loadAgents();
  }, []);

  useEffect(() => {
    let active = true;

    async function loadConversations() {
      try {
        const list = await getConversations();
        if (!active) return;

        setConversations(list);

        if (!selectedConversationId && list.length > 0) {
          const nextId = initialConversationId && list.some((item) => item.id === initialConversationId)
            ? initialConversationId
            : list[0].id;
          setSelectedConversationId(nextId);
        }
      } catch {
        if (active) setError("Failed to load conversations");
      }
    }

    void loadConversations();
    return () => {
      active = false;
    };
  }, [initialConversationId, selectedConversationId]);

  useEffect(() => {
    let active = true;

    async function loadMessages() {
      if (!selectedConversationId) {
        setMessages([]);
        return;
      }

      setLoadingMessages(true);
      setError(null);
      try {
        const list = await getConversationMessages(selectedConversationId);
        if (active) setMessages(list);
      } catch {
        if (active) setError("Failed to load messages");
      } finally {
        if (active) setLoadingMessages(false);
      }
    }

    void loadMessages();
    return () => {
      active = false;
    };
  }, [selectedConversationId]);

  const selectedConversation = useMemo(
    () => conversations.find((item) => item.id === selectedConversationId) ?? null,
    [conversations, selectedConversationId]
  );

  const selectedAgent = useMemo(
    () => agents.find((a) => a.id === selectedAgentId) ?? null,
    [agents, selectedAgentId]
  );

  async function handleCreateConversation() {
    /**
     * Function: handleCreateConversation
     * Description: Create a new conversation and navigate to its route.
     * Parameters:
     * Returns:
     *   Promise resolved after local state and route are updated.
     */
    setError(null);
    try {
      const created = await createConversation();
      setConversations((prev) => [created, ...prev]);
      setSelectedConversationId(created.id);
      setMessages([]);
      router.push(`/chat/${created.id}`);
    } catch {
      setError("Failed to create conversation");
    }
  }

  async function handleSend() {
    /**
     * Function: handleSend
     * Description: Send user message with optimistic UI, stream assistant output, and rollback on failure.
     * Parameters:
     * Returns:
     *   Promise resolved when sending lifecycle completes.
     */
    const content = draft.trim();
    if (!content || sending) return;

    setSending(true);
    setError(null);

    let targetConversationId = selectedConversationId;
    if (!targetConversationId) {
      try {
        const created = await createConversation();
        setConversations((prev) => [created, ...prev]);
        targetConversationId = created.id;
        setSelectedConversationId(created.id);
        router.push(`/chat/${created.id}`);
      } catch {
        setError("Failed to create conversation");
        setSending(false);
        return;
      }
    }

    const optimisticUserMessage: ChatMessage = {
      id: `tmp-user-${Date.now()}`,
      role: "user",
      content
    };
    const optimisticAssistantId = `tmp-assistant-${Date.now()}`;
    const optimisticAssistantMessage: ChatMessage = {
      id: optimisticAssistantId,
      role: "assistant",
      content: ""
    };

    setMessages((prev) => [...prev, optimisticUserMessage]);
    setMessages((prev) => [...prev, optimisticAssistantMessage]);
    setDraft("");

    try {
      await streamMessage(
        {
        conversationId: targetConversationId ?? undefined,
        message: content,
        agentId: selectedAgentId || undefined,
        },
        {
          onChunk: (chunk) => {
            setMessages((prev) =>
              prev.map((message) =>
                message.id === optimisticAssistantId
                  ? { ...message, content: `${message.content}${chunk}` }
                  : message
              )
            );
          },
          onDone: () => {
            setMessages((prev) =>
              prev.map((message) =>
                message.id === optimisticAssistantId && !message.content.trim()
                  ? { ...message, content: "No response returned" }
                  : message
              )
            );
          }
        }
      );
    } catch {
      setMessages((prev) =>
        prev.filter(
          (message) => message.id !== optimisticUserMessage.id && message.id !== optimisticAssistantId
        )
      );
      setError("Failed to send message");
    } finally {
      setSending(false);
    }
  }

  return (
    <section className="grid min-h-[calc(100vh-140px)] grid-cols-1 gap-4 lg:grid-cols-[300px_1fr]">
      <aside className="flex min-h-0 flex-col rounded-2xl border border-slate-800 bg-slate-900/70">
        <div className="flex items-center justify-between border-b border-slate-800 p-4">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300">Conversations</h2>
          <button
            type="button"
            onClick={handleCreateConversation}
            className="rounded-lg bg-sky-500 px-3 py-1.5 text-xs font-semibold text-white hover:bg-sky-400"
          >
            New
          </button>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto p-2">
          {conversations.length === 0 ? (
            <p className="px-2 py-3 text-sm text-slate-400">No conversations yet.</p>
          ) : (
            conversations.map((conversation) => {
              const active = conversation.id === selectedConversationId;
              return (
                <button
                  key={conversation.id}
                  type="button"
                  onClick={() => {
                    setSelectedConversationId(conversation.id);
                    router.push(`/chat/${conversation.id}`);
                  }}
                  className={`mb-1 w-full rounded-lg px-3 py-2 text-left text-sm transition ${
                    active
                      ? "bg-sky-500/20 text-sky-300 ring-1 ring-sky-500/30"
                      : "text-slate-200 hover:bg-slate-800"
                  }`}
                >
                  <p className="truncate font-medium">{conversation.title || "Untitled conversation"}</p>
                  <p className="mt-0.5 text-xs text-slate-400">
                    {conversation.last_message_at
                      ? new Date(conversation.last_message_at).toLocaleString()
                      : "No messages yet"}
                  </p>
                </button>
              );
            })
          )}
        </div>
      </aside>

      <div className="flex min-h-0 flex-col rounded-2xl border border-slate-800 bg-slate-900/70">
        <header className="border-b border-slate-800 px-5 py-4 flex items-center justify-between gap-4">
          <div className="min-w-0">
            <h1 className="text-lg font-semibold truncate">{selectedConversation?.title ?? "Professional Chat"}</h1>
            <p className="text-sm text-slate-400">AI assistant with conversation context and persistent history.</p>
          </div>

          {/* Agent selector */}
          {agents.length > 0 && (
            <div className="shrink-0 flex items-center gap-2">
              <label htmlFor="agent-select" className="text-xs text-slate-400 whitespace-nowrap">
                Agent:
              </label>
              <select
                id="agent-select"
                value={selectedAgentId}
                onChange={(e) => setSelectedAgentId(e.target.value)}
                className="rounded-lg border border-slate-700 bg-slate-800 px-2 py-1.5 text-xs text-slate-100 outline-none focus:border-sky-500"
              >
                {agents.map((agent) => (
                  <option key={agent.id} value={agent.id}>
                    {agent.name}
                  </option>
                ))}
              </select>
              {selectedAgent && (
                <span className="text-xs text-slate-500">{selectedAgent.model}</span>
              )}
            </div>
          )}
        </header>

        <div className="min-h-0 flex-1 space-y-3 overflow-y-auto px-5 py-4">
          {loadingMessages ? <p className="text-sm text-slate-400">Loading messages...</p> : null}
          {!loadingMessages && messages.length === 0 ? (
            <p className="text-sm text-slate-400">Start a new message to begin this conversation.</p>
          ) : null}

          {messages.map((message) => (
            <article
              key={message.id}
              className={`max-w-3xl rounded-2xl px-4 py-3 text-sm ${
                message.role === "user" ? "ml-auto bg-sky-500 text-white" : "bg-slate-800 text-slate-100"
              }`}
            >
              <p className="mb-1 text-[11px] uppercase tracking-wider opacity-75">{message.role}</p>
              <p className="whitespace-pre-wrap">{message.content}</p>
            </article>
          ))}
        </div>

        <footer className="border-t border-slate-800 p-4">
          {error ? <p className="mb-2 text-sm text-red-400">{error}</p> : null}
          <div className="flex items-end gap-2">
            <textarea
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Type your message..."
              className="min-h-12 flex-1 resize-none rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  void handleSend();
                }
              }}
            />
            <button
              type="button"
              onClick={() => void handleSend()}
              disabled={sending || !draft.trim()}
              className="rounded-xl bg-sky-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {sending ? "Sending..." : "Send"}
            </button>
          </div>
        </footer>
      </div>
    </section>
  );
}
