"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { createAgent } from "@/features/agents/services/agentService";

const models = ["gpt-4.1", "gpt-4o-mini", "r2", "claude-3-5-sonnet", "gemini-1.5-pro"] as const;

const toolOptions = ["Web Search", "Code Interpreter", "File Reader", "Database Query"] as const;

const knowledgeOptions = ["Company Docs", "Product FAQ", "Support Playbooks", "Legal Policies"] as const;

const memoryOptions = ["Session Memory", "Long-Term Memory", "No Memory"] as const;

type ModelOption = (typeof models)[number];
type ToolOption = (typeof toolOptions)[number];
type KnowledgeOption = (typeof knowledgeOptions)[number];
type MemoryOption = (typeof memoryOptions)[number];

interface AgentCreateFormState {
  name: string;
  description: string;
  model: ModelOption;
  systemPrompt: string;
  tools: ToolOption[];
  knowledgeBase: KnowledgeOption;
  memory: MemoryOption;
  instructions: string;
  temperature: number;
  maxTokens: number;
  isPublic: boolean;
}

export default function AgentsCreateRoute() {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState<AgentCreateFormState>({
    name: "",
    description: "",
    model: "gpt-4.1",
    systemPrompt: "You are ALICI, a helpful AI assistant.",
    tools: [toolOptions[0]],
    knowledgeBase: knowledgeOptions[0],
    memory: memoryOptions[0],
    instructions: "Respond clearly, safely, and focus on business outcomes.",
    temperature: 70,
    maxTokens: 1000,
    isPublic: false
  });

  function update<K extends keyof AgentCreateFormState>(key: K, value: AgentCreateFormState[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function toggleTool(tool: ToolOption) {
    setForm((prev) => {
      const enabled = prev.tools.includes(tool);
      if (enabled) {
        return { ...prev, tools: prev.tools.filter((item) => item !== tool) };
      }
      return { ...prev, tools: [...prev.tools, tool] };
    });
  }

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);

    if (!form.name.trim()) {
      setError("Agent Name is required.");
      setSubmitting(false);
      return;
    }

    try {
      await createAgent({
        name: form.name.trim(),
        description: form.description.trim() || undefined,
        system_prompt: `${form.systemPrompt.trim()}\n\nMemory: ${form.memory}\nKnowledge: ${form.knowledgeBase}\nTools: ${form.tools.join(", ")}\nInstructions: ${form.instructions.trim()}`,
        model: form.model,
        temperature: form.temperature,
        max_tokens: form.maxTokens,
        is_public: form.isPublic
      });

      router.push("/agents");
    } catch {
      setError("Failed to create agent. Please try again.");
      setSubmitting(false);
    }
  }

  return (
      <section className="space-y-6">
        <header className="flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-widest text-slate-400">Agents</p>
            <h1 className="text-2xl font-semibold">Create Agent</h1>
            <p className="mt-1 text-sm text-slate-300">
              Build a custom AI agent with model, tools, knowledge, memory, and instructions.
            </p>
          </div>
          <Link
            href="/agents"
            className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-slate-200 hover:bg-slate-800"
          >
            Back to Agents
          </Link>
        </header>

        <form onSubmit={onSubmit} className="grid gap-6 lg:grid-cols-3">
          <div className="space-y-4 lg:col-span-2">
            <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
              <h2 className="mb-4 text-lg font-semibold">Agent Profile</h2>
              <div className="grid gap-4 md:grid-cols-2">
                <label className="flex flex-col gap-2 md:col-span-2">
                  <span className="text-sm text-slate-300">Agent Name</span>
                  <input
                    value={form.name}
                    onChange={(event) => update("name", event.target.value)}
                    className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
                    placeholder="Support Expert"
                    required
                  />
                </label>

                <label className="flex flex-col gap-2 md:col-span-2">
                  <span className="text-sm text-slate-300">Agent Description</span>
                  <textarea
                    value={form.description}
                    onChange={(event) => update("description", event.target.value)}
                    className="min-h-24 rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
                    placeholder="Handles customer support and onboarding questions."
                  />
                </label>

                <label className="flex flex-col gap-2">
                  <span className="text-sm text-slate-300">Model</span>
                  <select
                    value={form.model}
                    onChange={(event) => update("model", event.target.value as ModelOption)}
                    className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
                  >
                    {models.map((model) => (
                      <option key={model} value={model}>
                        {model}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="flex flex-col gap-2">
                  <span className="text-sm text-slate-300">Knowledge Base</span>
                  <select
                    value={form.knowledgeBase}
                    onChange={(event) => update("knowledgeBase", event.target.value as KnowledgeOption)}
                    className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
                  >
                    {knowledgeOptions.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="flex flex-col gap-2">
                  <span className="text-sm text-slate-300">Memory</span>
                  <select
                    value={form.memory}
                    onChange={(event) => update("memory", event.target.value as MemoryOption)}
                    className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
                  >
                    {memoryOptions.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="flex flex-col gap-2">
                  <span className="text-sm text-slate-300">Temperature</span>
                  <input
                    type="number"
                    min={0}
                    max={100}
                    value={form.temperature}
                    onChange={(event) => update("temperature", Number(event.target.value))}
                    className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
                  />
                </label>

                <label className="flex flex-col gap-2">
                  <span className="text-sm text-slate-300">Max Tokens</span>
                  <input
                    type="number"
                    min={128}
                    max={8000}
                    value={form.maxTokens}
                    onChange={(event) => update("maxTokens", Number(event.target.value))}
                    className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
                  />
                </label>

                <label className="flex items-center gap-2 md:col-span-2">
                  <input
                    type="checkbox"
                    checked={form.isPublic}
                    onChange={(event) => update("isPublic", event.target.checked)}
                    className="h-4 w-4 rounded border-slate-600 bg-slate-950"
                  />
                  <span className="text-sm text-slate-300">Make this agent public</span>
                </label>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
              <h2 className="mb-4 text-lg font-semibold">Behavior</h2>
              <div className="space-y-4">
                <label className="flex flex-col gap-2">
                  <span className="text-sm text-slate-300">System Prompt</span>
                  <textarea
                    value={form.systemPrompt}
                    onChange={(event) => update("systemPrompt", event.target.value)}
                    className="min-h-28 rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
                    placeholder="Define global behavior for the assistant."
                  />
                </label>

                <label className="flex flex-col gap-2">
                  <span className="text-sm text-slate-300">Instructions</span>
                  <textarea
                    value={form.instructions}
                    onChange={(event) => update("instructions", event.target.value)}
                    className="min-h-24 rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 outline-none focus:border-sky-500"
                    placeholder="Specific execution instructions and constraints."
                  />
                </label>
              </div>
            </div>
          </div>

          <aside className="space-y-4">
            <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
              <h2 className="mb-3 text-lg font-semibold">Tools</h2>
              <div className="space-y-2">
                {toolOptions.map((tool) => {
                  const selected = form.tools.includes(tool);
                  return (
                    <button
                      key={tool}
                      type="button"
                      onClick={() => toggleTool(tool)}
                      className={`w-full rounded-lg border px-3 py-2 text-left text-sm transition ${
                        selected
                          ? "border-sky-500/40 bg-sky-500/10 text-sky-300"
                          : "border-slate-700 text-slate-200 hover:bg-slate-800"
                      }`}
                    >
                      {tool}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
              <h2 className="mb-3 text-lg font-semibold">Publish</h2>
              <p className="mb-4 text-sm text-slate-400">
                Save your agent profile and start using it across chat, automation, and API calls.
              </p>
              {error && <p className="mb-3 text-sm text-red-400">{error}</p>}
              <button
                type="submit"
                disabled={submitting}
                className="w-full rounded-lg bg-sky-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-sky-400 disabled:cursor-not-allowed disabled:opacity-70"
              >
                {submitting ? "Creating..." : "Create Agent"}
              </button>
            </div>
          </aside>
        </form>
      </section>
  );
}
