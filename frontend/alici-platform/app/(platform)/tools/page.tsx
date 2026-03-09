"use client";

import { useEffect, useState } from "react";
import { api } from "@/services/api";

const toolDescriptions: Record<string, { label: string; description: string; icon: string }> = {
  web_search: {
    label: "Web Search",
    description: "Search the internet for real-time information and news.",
    icon: "🌐"
  },
  database_query: {
    label: "Database Query",
    description: "Execute SQL queries against connected data sources.",
    icon: "🗄️"
  },
  send_email: {
    label: "Send Email",
    description: "Compose and send email messages via SMTP or API.",
    icon: "📧"
  },
  execute_code: {
    label: "Python Interpreter",
    description: "Execute Python code snippets in a sandboxed environment.",
    icon: "🐍"
  },
  http_request: {
    label: "HTTP Request",
    description: "Make HTTP requests to external APIs and webhooks.",
    icon: "🔗"
  },
  file_read: {
    label: "File Reader",
    description: "Read and parse files from storage or knowledge base.",
    icon: "📄"
  },
  generate_document: {
    label: "Document Generator",
    description: "Generate structured documents, reports, and exports.",
    icon: "📝"
  }
};

export default function ToolsRoute() {
  const [tools, setTools] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState<string | null>(null);
  const [result, setResult] = useState<{ tool: string; output: string } | null>(null);

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const res = await api.get<{ data: { tools: string[] } }>("/tools");
        const data = res.data?.data ?? res.data;
        if (active) {
          setTools(data?.tools ?? []);
        }
      } catch {
        // Show fallback list
        if (active) {
          setTools(Object.keys(toolDescriptions));
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    void load();
    return () => {
      active = false;
    };
  }, []);

  async function handleRun(tool: string) {
    setRunning(tool);
    setResult(null);
    try {
      const res = await api.post<{ data: Record<string, unknown> }>("/tools/run", {
        tool,
        input: `Test run of ${tool}`
      });
      const output = JSON.stringify(res.data?.data ?? res.data, null, 2);
      setResult({ tool, output });
    } catch {
      setResult({ tool, output: "Error running tool. Check authentication and try again." });
    } finally {
      setRunning(null);
    }
  }

  return (
      <section className="space-y-6">
        <header>
          <p className="text-xs uppercase tracking-widest text-slate-400">Capabilities</p>
          <h1 className="text-2xl font-semibold">Tools Catalog</h1>
          <p className="mt-1 text-sm text-slate-400">
            Activate and manage tools available to your agents. Each tool extends what AI can do on your behalf.
          </p>
        </header>

        {loading ? (
          <p className="text-sm text-slate-400">Loading tools catalog...</p>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {tools.map((tool) => {
              const info = toolDescriptions[tool] ?? {
                label: tool,
                description: "Custom tool.",
                icon: "⚙️"
              };
              const isRunning = running === tool;

              return (
                <article
                  key={tool}
                  className="flex flex-col rounded-2xl border border-slate-800 bg-slate-900/70 p-5 transition hover:border-slate-700"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{info.icon}</span>
                    <div>
                      <h3 className="font-semibold text-slate-100">{info.label}</h3>
                      <p className="mt-0.5 text-xs text-slate-400">{info.description}</p>
                    </div>
                  </div>

                  <button
                    type="button"
                    disabled={isRunning || running !== null}
                    onClick={() => void handleRun(tool)}
                    className="mt-4 rounded-lg border border-slate-700 px-3 py-2 text-xs font-medium text-slate-200 transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {isRunning ? "Running..." : "Test Tool"}
                  </button>
                </article>
              );
            })}
          </div>
        )}

        {result && (
          <div className="rounded-2xl border border-slate-700 bg-slate-900 p-5">
            <p className="mb-2 text-xs font-semibold uppercase tracking-widest text-slate-400">
              Result: {toolDescriptions[result.tool]?.label ?? result.tool}
            </p>
            <pre className="overflow-x-auto whitespace-pre-wrap text-xs text-slate-300">
              {result.output}
            </pre>
          </div>
        )}
      </section>
  );
}
