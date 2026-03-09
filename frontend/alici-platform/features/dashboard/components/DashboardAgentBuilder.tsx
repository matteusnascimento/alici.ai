"use client";

import { useState } from "react";
import { Bot, Brain, Database, Globe, Code, FileText, Wrench } from "lucide-react";
import { createAgent } from "@/features/agents/services/agentService";

const MODELS = ["gpt-4.1", "gpt-4o-mini", "claude-3-5-sonnet", "gemini-1.5-pro", "r2"] as const;
const MEMORY_OPTIONS = ["Session Memory", "Long-Term Memory", "No Memory"] as const;
const KNOWLEDGE_OPTIONS = ["Company Docs", "Product FAQ", "Support Playbooks", "Legal Policies"] as const;

type ModelOption = (typeof MODELS)[number];
type MemoryOption = (typeof MEMORY_OPTIONS)[number];
type KnowledgeOption = (typeof KNOWLEDGE_OPTIONS)[number];

interface Tool { id: string; label: string; icon: React.ReactNode }

const TOOLS: Tool[] = [
  { id: "web_search",       label: "Web Search",      icon: <Globe size={13} /> },
  { id: "code_interpreter", label: "Code Interpreter", icon: <Code size={13} /> },
  { id: "file_reader",      label: "File Reader",      icon: <FileText size={13} /> },
  { id: "database_query",   label: "Database Query",   icon: <Database size={13} /> },
];

interface Form {
  name: string;
  description: string;
  instructions: string;
  model: ModelOption;
  memory: MemoryOption;
  knowledgeBase: KnowledgeOption;
  tools: string[];
}

interface PreviewMsg { role: "user" | "assistant"; content: string }

export function DashboardAgentBuilder() {
  const [form, setForm] = useState<Form>({
    name: "",
    description: "",
    instructions: "You are ALICI, a helpful AI assistant. Respond clearly and focus on business outcomes.",
    model: "gpt-4.1",
    memory: "Session Memory",
    knowledgeBase: "Company Docs",
    tools: [],
  });
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [previewInput, setPreviewInput] = useState("");
  const [previewMsgs, setPreviewMsgs] = useState<PreviewMsg[]>([]);

  function set<K extends keyof Form>(k: K, v: Form[K]) {
    setForm((p: Form) => ({ ...p, [k]: v }));
  }

  function toggleTool(id: string) {
    setForm((p: Form) => ({
      ...p,
      tools: p.tools.includes(id) ? p.tools.filter((t: string) => t !== id) : [...p.tools, id],
    }));
  }

  function sendPreview() {
    const text = previewInput.trim();
    if (!text || !form.name) return;
    setPreviewMsgs((p: PreviewMsg[]) => [
      ...p,
      { role: "user", content: text },
      { role: "assistant", content: `Olá! Sou ${form.name}. ${form.description || "Como posso ajudar?"}` },
    ]);
    setPreviewInput("");
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name.trim()) { setError("Agent Name é obrigatório."); return; }
    setSubmitting(true);
    setError(null);
    setSuccess(false);
    try {
      await createAgent({
        name: form.name.trim(),
        description: form.description.trim() || undefined,
        system_prompt: `${form.instructions}\n\nMemory: ${form.memory}\nKnowledge: ${form.knowledgeBase}\nTools: ${form.tools.join(", ")}`,
        model: form.model,
        is_public: false,
      });
      setSuccess(true);
      setForm({ name: "", description: "", instructions: form.instructions, model: form.model, memory: form.memory, knowledgeBase: form.knowledgeBase, tools: [] });
      setPreviewMsgs([]);
    } catch {
      setError("Falha ao criar agente. Tente novamente.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_340px]">
      {/* ── Left: form ── */}
      <form onSubmit={(e: React.FormEvent) => void handleSubmit(e)} className="space-y-4">

        {/* Profile */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 space-y-3">
          <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2"><Bot size={15} className="text-sky-400" />Agent Profile</h3>
          <label className="flex flex-col gap-1">
            <span className="text-xs text-slate-400">Agent Name *</span>
            <input value={form.name} onChange={(e: React.ChangeEvent<HTMLInputElement>) => set("name", e.target.value)} required
              placeholder="e.g. Support Expert"
              className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500" />
          </label>
          <label className="flex flex-col gap-1">
            <span className="text-xs text-slate-400">Description</span>
            <input value={form.description} onChange={(e: React.ChangeEvent<HTMLInputElement>) => set("description", e.target.value)}
              placeholder="Describe what this agent does"
              className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500" />
          </label>
        </div>

        {/* Instructions */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 space-y-2">
          <h3 className="text-sm font-semibold text-slate-200">Instructions (System Prompt)</h3>
          <textarea value={form.instructions} onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => set("instructions", e.target.value)}
            rows={4} placeholder="Define the agent's persona and behavior..."
            className="w-full resize-none rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500" />
        </div>

        {/* Model & Memory */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 space-y-3">
          <h3 className="text-sm font-semibold text-slate-200">Model & Memory</h3>
          <div className="grid gap-3 sm:grid-cols-2">
            <label className="flex flex-col gap-1">
              <span className="text-xs text-slate-400">Model</span>
              <select value={form.model} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => set("model", e.target.value as ModelOption)}
                className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500">
                {MODELS.map((m) => <option key={m}>{m}</option>)}
              </select>
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-xs text-slate-400 flex items-center gap-1"><Brain size={11} />Memory</span>
              <select value={form.memory} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => set("memory", e.target.value as MemoryOption)}
                className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500">
                {MEMORY_OPTIONS.map((m) => <option key={m}>{m}</option>)}
              </select>
            </label>
          </div>
        </div>

        {/* Tools */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 space-y-3">
          <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2"><Wrench size={14} />Tools</h3>
          <div className="flex flex-wrap gap-2">
            {TOOLS.map((t) => {
              const on = form.tools.includes(t.id);
              return (
                <button key={t.id} type="button" onClick={() => toggleTool(t.id)}
                  className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition ${on ? "border-sky-500/50 bg-sky-500/10 text-sky-300" : "border-slate-700 text-slate-300 hover:bg-slate-800"}`}>
                  {t.icon}{t.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Knowledge */}
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 p-4 space-y-2">
          <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2"><Database size={14} />Knowledge Base</h3>
          <select value={form.knowledgeBase} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => set("knowledgeBase", e.target.value as KnowledgeOption)}
            className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500">
            {KNOWLEDGE_OPTIONS.map((k) => <option key={k}>{k}</option>)}
          </select>
        </div>

        {/* Submit */}
        {error   && <p className="text-sm text-red-400">{error}</p>}
        {success && <p className="text-sm text-emerald-400">✓ Agente criado com sucesso!</p>}
        <button type="submit" disabled={submitting}
          className="w-full rounded-xl bg-sky-500 py-2.5 text-sm font-semibold text-white transition hover:bg-sky-400 disabled:opacity-60">
          {submitting ? "Criando agente..." : "🤖 Create Agent"}
        </button>
      </form>

      {/* ── Right: live preview ── */}
      <div className="flex flex-col rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden">
        <div className="border-b border-slate-800 px-4 py-3 flex items-center gap-2">
          <span className="h-2 w-2 rounded-full bg-emerald-400" />
          <span className="text-xs font-semibold text-slate-300">Preview</span>
          <span className="ml-auto text-xs text-slate-500 truncate">{form.name || "Unnamed"} · {form.model}</span>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-2 min-h-48">
          {previewMsgs.length === 0 ? (
            <div className="flex h-full flex-col items-center justify-center gap-2 text-center py-8">
              <Bot size={28} className="text-slate-600" />
              <p className="text-xs text-slate-500">{form.name ? `Teste o ${form.name}` : "Preencha o nome para testar"}</p>
            </div>
          ) : previewMsgs.map((m, i) => (
            <div key={i} className={`max-w-[85%] rounded-2xl px-3 py-2 text-sm ${m.role === "user" ? "ml-auto bg-sky-500 text-white" : "bg-slate-800 text-slate-100"}`}>
              {m.content}
            </div>
          ))}
        </div>
        <div className="border-t border-slate-800 p-3 flex gap-2">
          <input value={previewInput} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPreviewInput(e.target.value)}
            onKeyDown={(e: React.KeyboardEvent) => { if (e.key === "Enter") sendPreview(); }}
            placeholder="Envie uma mensagem de teste..." disabled={!form.name}
            className="flex-1 rounded-lg border border-slate-700 bg-slate-950 px-3 py-1.5 text-sm text-slate-100 outline-none focus:border-sky-500 disabled:opacity-40" />
          <button type="button" onClick={sendPreview} disabled={!previewInput.trim() || !form.name}
            className="rounded-lg bg-sky-500 px-3 py-1.5 text-sm font-semibold text-white disabled:opacity-40">
            →
          </button>
        </div>
      </div>
    </div>
  );
}
