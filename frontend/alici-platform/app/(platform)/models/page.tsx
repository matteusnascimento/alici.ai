"use client";

import { useEffect, useState } from "react";
import { api } from "@/services/api";

interface ModelItem {
  id: string;
  provider: string;
  supports_stream: boolean;
}

interface ModelsResponse {
  selected: string;
  items: ModelItem[];
}

const providerColors: Record<string, string> = {
  openai: "text-emerald-400",
  deepseek: "text-blue-400",
  local: "text-amber-400"
};

export default function ModelsRoute() {
  const [models, setModels] = useState<ModelItem[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const res = await api.get<{ data: ModelsResponse }>("/models");
        const data = res.data?.data ?? res.data;
        if (active) {
          setModels(data?.items ?? []);
          setSelected(data?.selected ?? "");
        }
      } catch {
        // Keep empty state on error
      } finally {
        if (active) setLoading(false);
      }
    }

    void load();
    return () => {
      active = false;
    };
  }, []);

  async function handleSelect(modelId: string) {
    setSaving(true);
    setSaved(false);
    try {
      await api.post("/models/select", { model: modelId });
      setSelected(modelId);
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch {
      // ignore
    } finally {
      setSaving(false);
    }
  }

  return (
      <section className="space-y-6">
        <header>
          <p className="text-xs uppercase tracking-widest text-slate-400">Configuration</p>
          <h1 className="text-2xl font-semibold">AI Models</h1>
          <p className="mt-1 text-sm text-slate-400">
            Select which language model the platform will use for completions and agents.
          </p>
        </header>

        {saved && (
          <p className="text-sm text-emerald-400">Model selection saved successfully.</p>
        )}

        {loading ? (
          <p className="text-sm text-slate-400">Loading available models...</p>
        ) : models.length === 0 ? (
          <p className="text-sm text-slate-400">No models available. Configure your API keys in Settings.</p>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            {models.map((model) => {
              const isActive = model.id === selected;
              const colorClass = providerColors[model.provider] ?? "text-slate-300";

              return (
                <article
                  key={model.id}
                  className={`rounded-2xl border p-5 transition ${
                    isActive
                      ? "border-sky-500/60 bg-sky-500/10"
                      : "border-slate-800 bg-slate-900/70 hover:border-slate-700"
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h3 className="font-semibold text-slate-100">{model.id}</h3>
                      <p className={`mt-1 text-xs font-medium ${colorClass}`}>{model.provider}</p>
                    </div>
                    {isActive && (
                      <span className="rounded-full bg-sky-500/20 px-2 py-0.5 text-xs text-sky-300 ring-1 ring-sky-500/40">
                        Active
                      </span>
                    )}
                  </div>

                  <p className="mt-3 text-xs text-slate-400">
                    Streaming: {model.supports_stream ? "✓ Supported" : "✗ Not supported"}
                  </p>

                  <button
                    type="button"
                    disabled={saving || isActive}
                    onClick={() => void handleSelect(model.id)}
                    className={`mt-4 w-full rounded-lg px-3 py-2 text-sm font-semibold transition ${
                      isActive
                        ? "cursor-default bg-sky-500/20 text-sky-300"
                        : "bg-slate-800 text-slate-100 hover:bg-slate-700 disabled:opacity-60"
                    }`}
                  >
                    {isActive ? "Selected" : saving ? "Saving..." : "Select Model"}
                  </button>
                </article>
              );
            })}
          </div>
        )}
      </section>
  );
}
