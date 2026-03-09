"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Bot, Brain, Database, Globe, Wrench, Code, FileText } from "lucide-react";
import { createAgent } from "@/features/agents/services/agentService";

const models = ["gpt-4.1", "gpt-4o-mini", "r2", "claude-3-5-sonnet", "gemini-1.5-pro"] as const;
const memoryOptions = ["Session Memory", "Long-Term Memory", "No Memory"] as const;
const knowledgeOptions = ["Company Docs", "Product FAQ", "Support Playbooks", "Legal Policies"] as const;

type ModelOption = (typeof models)[number];
type MemoryOption = (typeof memoryOptions)[number];
type KnowledgeOption = (typeof knowledgeOptions)[number];

interface Tool {
  id: string;
  label: string;
  icon: React.ReactNode;
  description: string;
}

const TOOLS: Tool[] = [
  { id: "web_search",       label: "Web Search",       icon: <Globe size={14} />,    description: "Search the internet in real-time" },
  { id: "code_interpreter", label: "Code Interpreter",  icon: <Code size={14} />,     description: "Execute and debug code" },
  { id: "file_reader",      label: "File Reader",       icon: <FileText size={14} />, description: "Read and parse uploaded files" },
  { id: "database_query",   label: "Database Query",    icon: <Database size={14} />, description: "Query connected data sources" },
];

interface AgentForm {
  name: string;
  description: string;
  instructions: string;
  model: ModelOption;
  memory: MemoryOption;
  knowledgeBase: KnowledgeOption;
  tools: string[];
  isPublic: boolean;
}

interface PreviewMessage {
  role: "user" | "assistant";
  content: string;
}

export default function AgentsCreateRoute() {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewInput, setPreviewInput] = useState("");
  const [previewMessages, setPreviewMessages] = useState<PreviewMessage[]>([]);

  const [form, setForm] = useState<AgentForm>({
    name: "",
    description: "",
    instructions: "You are ALICI, a helpful AI assistant. Respond clearly, safely, and focus on business outcomes.",
    model: "gpt-4.1",
    memory: "Session Memory",
    knowledgeBase: "Company Docs",
    tools: ["web_search"],
    isPublic: false,
  });

  function set<K extends keyof AgentForm>(key: K, value: AgentForm[K]) {
    setForm((prev: AgentForm) => ({ ...prev, [key]: value }));
  }

  function toggleTool(id: string) {
    setForm((prev: AgentForm) => {
      const active = prev.tools.includes(id);
      return {
        ...prev,
        tools: active ? prev.tools.filter((t: string) => t !== id) : [...prev.tools, id],
      };
    });
  }

  function handlePreviewSend() {
    const text = previewInput.trim();
    if (!text) return;
    const agentName = form.name || "Agent";
    setPreviewMessages((prev: PreviewMessage[]) => [
      ...prev,
      { role: "user", content: text },
      {
        role: "assistant",
        content: `Hi! I'm ${agentName}. ${form.description ? form.description + " " : ""}How can I help you today?`,
      },
    ]);
    setPreviewInput("");
  }

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!form.name.trim()) { setError("Agent Name is required."); return; }
    setSubmitting(true);
    setError(null);
    try {
      await createAgent({
        name: form.name.trim(),
        description: form.description.trim() || undefined,
        system_prompt: `${form.instructions.trim()}\n\nMemory: ${form.memory}\nKnowledge: ${form.knowledgeBase}\nTools: ${form.tools.join(", ")}`,
        model: form.model,
        temperature: 70,  // backend stores 0-100 and converts to 0-1 on AI call
        max_tokens: 1000,
        is_public: form.isPublic,
      });
      router.push("/agents");
    } catch {
      setError("Failed to create agent. Please try again.");
      setSubmitting(false);
    }
  }

  return (
    <section className="space-y-6">
      {/* Header */}
      <header className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Bot size={24} className="text-sky-400" />
          <div>
            <p className="text-xs uppercase tracking-widest text-slate-400">Agents</p>
            <h1 className="text-2xl font-semibold">Create Agent</h1>
          </div>
        </div>
        <Link
          href="/agents"
          className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-slate-800"
        >
          ← Back to Agents
        </Link>
      </header>

      <form onSubmit={(e: React.FormEvent<HTMLFormElement>) => void onSubmit(e)}
            className="grid gap-6 xl:grid-cols-[1fr_380px]">

        {/* ── Left column: builder ── */}
        <div className="space-y-4">

          {/* 1 · Profile */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5 space-y-4">
            <h2 className="font-semibold text-slate-200">Agent Profile</h2>

            <label className="flex flex-col gap-1.5">
              <span className="text-xs text-slate-400">Agent Name *</span>
              <input
                value={form.name}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => set("name", e.target.value)}
                required
                placeholder="e.g. Support Expert"
                className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
              />
            </label>

            <label className="flex flex-col gap-1.5">
              <span className="text-xs text-slate-400">Description</span>
              <textarea
                value={form.description}
                onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => set("description", e.target.value)}
                rows={2}
                placeholder="What does this agent do?"
                className="resize-none rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
              />
            </label>
          </div>

          {/* 2 · Instructions */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5 space-y-3">
            <h2 className="font-semibold text-slate-200">Instructions (System Prompt)</h2>
            <textarea
              value={form.instructions}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => set("instructions", e.target.value)}
              rows={5}
              placeholder="Define the agent's persona, rules, and goals..."
              className="w-full resize-none rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
            />
          </div>

          {/* 3 · Model & Memory */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5 space-y-4">
            <h2 className="font-semibold text-slate-200">Model & Memory</h2>
            <div className="grid gap-4 sm:grid-cols-2">
              <label className="flex flex-col gap-1.5">
                <span className="text-xs text-slate-400">Model</span>
                <select
                  value={form.model}
                  onChange={(e: React.ChangeEvent<HTMLSelectElement>) => set("model", e.target.value as ModelOption)}
                  className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
                >
                  {models.map((m) => <option key={m}>{m}</option>)}
                </select>
              </label>

              <label className="flex flex-col gap-1.5">
                <span className="text-xs text-slate-400 flex items-center gap-1"><Brain size={12} />Memory</span>
                <select
                  value={form.memory}
                  onChange={(e: React.ChangeEvent<HTMLSelectElement>) => set("memory", e.target.value as MemoryOption)}
                  className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
                >
                  {memoryOptions.map((m) => <option key={m}>{m}</option>)}
                </select>
              </label>
            </div>
          </div>

          {/* 4 · Tools */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5 space-y-3">
            <h2 className="font-semibold text-slate-200 flex items-center gap-2"><Wrench size={16} />Tools</h2>
            <div className="grid gap-2 sm:grid-cols-2">
              {TOOLS.map((tool) => {
                const active = form.tools.includes(tool.id);
                return (
                  <button
                    key={tool.id}
                    type="button"
                    onClick={() => toggleTool(tool.id)}
                    className={`flex items-start gap-2 rounded-xl border p-3 text-left transition ${
                      active
                        ? "border-sky-500/50 bg-sky-500/10 text-sky-300"
                        : "border-slate-700 text-slate-300 hover:bg-slate-800"
                    }`}
                  >
                    <span className="mt-0.5">{tool.icon}</span>
                    <div>
                      <p className="text-sm font-medium leading-tight">{tool.label}</p>
                      <p className="text-xs text-slate-500">{tool.description}</p>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* 5 · Knowledge */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5 space-y-3">
            <h2 className="font-semibold text-slate-200 flex items-center gap-2"><Database size={16} />Knowledge</h2>
            <select
              value={form.knowledgeBase}
              onChange={(e: React.ChangeEvent<HTMLSelectElement>) => set("knowledgeBase", e.target.value as KnowledgeOption)}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
            >
              {knowledgeOptions.map((k) => <option key={k}>{k}</option>)}
            </select>
            <p className="text-xs text-slate-500">Attach a knowledge source for RAG-based retrieval.</p>
          </div>

          {/* 6 · Publish */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5 space-y-4">
            <h2 className="font-semibold text-slate-200">Publish</h2>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={form.isPublic}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => set("isPublic", e.target.checked)}
                className="h-4 w-4 rounded border-slate-600 bg-slate-950"
              />
              <span className="text-sm text-slate-300">Make this agent public (visible in Marketplace)</span>
            </label>
            {error && <p className="text-sm text-red-400">{error}</p>}
            <button
              type="submit"
              disabled={submitting}
              className="w-full rounded-xl bg-sky-500 py-2.5 text-sm font-semibold text-white transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {submitting ? "Creating agent..." : "🤖 Create Agent"}
            </button>
          </div>
        </div>

        {/* ── Right column: live preview ── */}
        <aside className="flex flex-col rounded-2xl border border-slate-800 bg-slate-900/70 overflow-hidden">
          <div className="border-b border-slate-800 px-4 py-3 flex items-center gap-2">
            <div className="h-2 w-2 rounded-full bg-emerald-400" />
            <span className="text-xs font-semibold text-slate-300">Preview</span>
            <span className="ml-auto text-xs text-slate-500">{form.name || "Unnamed agent"} · {form.model}</span>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-64">
            {previewMessages.length === 0 ? (
              <div className="flex h-full flex-col items-center justify-center gap-2 text-center">
                <Bot size={32} className="text-slate-600" />
                <p className="text-sm text-slate-500">
                  {form.name
                    ? `Test your conversation with ${form.name}`
                    : "Fill in the agent name to start the preview"}
                </p>
              </div>
            ) : (
              previewMessages.map((msg, i) => (
                <div
                  key={i}
                  className={`max-w-[85%] rounded-2xl px-3 py-2 text-sm ${
                    msg.role === "user"
                      ? "ml-auto bg-sky-500 text-white"
                      : "bg-slate-800 text-slate-100"
                  }`}
                >
                  {msg.content}
                </div>
              ))
            )}
          </div>

          <div className="border-t border-slate-800 p-3 flex gap-2">
            <input
              value={previewInput}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPreviewInput(e.target.value)}
              onKeyDown={(e: React.KeyboardEvent<HTMLInputElement>) => { if (e.key === "Enter") handlePreviewSend(); }}
              placeholder="Send a test message..."
              className="flex-1 rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
            />
            <button
              type="button"
              onClick={handlePreviewSend}
              disabled={!previewInput.trim() || !form.name}
              className="rounded-lg bg-sky-500 px-3 py-2 text-sm font-semibold text-white disabled:opacity-40"
            >
              Send
            </button>
          </div>
        </aside>
      </form>
    </section>
  );
}
