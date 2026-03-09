"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Bot, Brain, Database, Globe, Wrench, Code, FileText } from "lucide-react";
import { api } from "@/services/api";
import type { ApiEnvelope } from "@/types/api";

interface AgentDetailRouteProps {
  params: { id: string };
}

const models = ["gpt-4.1", "gpt-4o-mini", "r2", "claude-3-5-sonnet", "gemini-1.5-pro"] as const;
type ModelOption = (typeof models)[number];

interface AgentForm {
  name: string;
  description: string;
  instructions: string;
  model: string;
  tools: string[];
  isPublic: boolean;
}

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

interface AgentData {
  id: string;
  name: string;
  description?: string;
  instructions?: string;
  model?: string;
  tools?: string[];
  is_public?: boolean;
}

export default function AgentDetailRoute({ params }: AgentDetailRouteProps) {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  const [form, setForm] = useState<AgentForm>({
    name: "",
    description: "",
    instructions: "",
    model: "gpt-4.1",
    tools: [],
    isPublic: false,
  });

  useEffect(() => {
    let active = true;

    async function load() {
      setLoading(true);
      try {
        const res = await api.get<ApiEnvelope<AgentData>>(`/agents/${params.id}`);
        const agent = res.data?.data;
        if (active && agent) {
          setForm({
            name: agent.name ?? "",
            description: agent.description ?? "",
            instructions: agent.instructions ?? "",
            model: agent.model ?? "gpt-4.1",
            tools: Array.isArray(agent.tools) ? agent.tools : [],
            isPublic: agent.is_public ?? false,
          });
        }
      } catch {
        if (active) setError("Failed to load agent.");
      } finally {
        if (active) setLoading(false);
      }
    }

    void load();
    return () => { active = false; };
  }, [params.id]);

  function set<K extends keyof AgentForm>(key: K, value: AgentForm[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function toggleTool(id: string) {
    setForm((prev) => {
      const active = prev.tools.includes(id);
      return { ...prev, tools: active ? prev.tools.filter((t) => t !== id) : [...prev.tools, id] };
    });
  }

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!form.name.trim()) { setError("Agent Name is required."); return; }
    setSubmitting(true);
    setError(null);
    setSaved(false);
    try {
      await api.put(`/agents/${params.id}`, {
        name: form.name.trim(),
        description: form.description.trim() || undefined,
        instructions: form.instructions.trim(),
        model: form.model,
        tools: form.tools,
        is_public: form.isPublic,
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch {
      setError("Failed to update agent. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) {
    return (
      <section className="space-y-6">
        <p className="text-sm text-slate-400">Loading agent...</p>
      </section>
    );
  }

  return (
    <section className="space-y-6">
      <header className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Bot size={24} className="text-sky-400" />
          <div>
            <p className="text-xs uppercase tracking-widest text-slate-400">Agents</p>
            <h1 className="text-2xl font-semibold">Edit Agent</h1>
          </div>
        </div>
        <Link
          href="/agents"
          className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-slate-800"
        >
          ← Back to Agents
        </Link>
      </header>

      <form onSubmit={(e) => void onSubmit(e)} className="space-y-4">
        {/* Profile */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5 space-y-4">
          <h2 className="font-semibold text-slate-200">Agent Profile</h2>
          <label className="flex flex-col gap-1.5">
            <span className="text-xs text-slate-400">Agent Name *</span>
            <input
              value={form.name}
              onChange={(e) => set("name", e.target.value)}
              required
              placeholder="e.g. Support Expert"
              className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
            />
          </label>
          <label className="flex flex-col gap-1.5">
            <span className="text-xs text-slate-400">Description</span>
            <textarea
              value={form.description}
              onChange={(e) => set("description", e.target.value)}
              rows={2}
              placeholder="What does this agent do?"
              className="resize-none rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
            />
          </label>
        </div>

        {/* Instructions */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5 space-y-3">
          <h2 className="font-semibold text-slate-200">Instructions (System Prompt)</h2>
          <textarea
            value={form.instructions}
            onChange={(e) => set("instructions", e.target.value)}
            rows={5}
            placeholder="Define the agent's persona, rules, and goals..."
            className="w-full resize-none rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
          />
        </div>

        {/* Model */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5 space-y-3">
          <h2 className="font-semibold text-slate-200">Model</h2>
          <select
            value={form.model}
            onChange={(e) => set("model", e.target.value as ModelOption)}
            className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
          >
            {models.map((m) => <option key={m}>{m}</option>)}
          </select>
        </div>

        {/* Tools */}
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

        {/* Publish */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5 space-y-4">
          <h2 className="font-semibold text-slate-200">Publish</h2>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={form.isPublic}
              onChange={(e) => set("isPublic", e.target.checked)}
              className="h-4 w-4 rounded border-slate-600 bg-slate-950"
            />
            <span className="text-sm text-slate-300">Make this agent public</span>
          </label>
          {error && <p className="text-sm text-red-400">{error}</p>}
          {saved && <p className="text-sm text-emerald-400">Agent updated successfully.</p>}
          <div className="flex gap-3">
            <button
              type="submit"
              disabled={submitting}
              className="rounded-xl bg-sky-500 px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {submitting ? "Saving..." : "Update Agent"}
            </button>
            <button
              type="button"
              onClick={() => router.push("/agents")}
              className="rounded-xl border border-slate-700 px-6 py-2.5 text-sm font-medium text-slate-200 hover:bg-slate-800"
            >
              Cancel
            </button>
          </div>
        </div>
      </form>
    </section>
  );
}

