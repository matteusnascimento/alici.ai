import { Database } from "lucide-react";

const PROVIDERS = [
  { name: "Supabase Vector", status: "Configurável", desc: "pgvector nativo no Postgres" },
  { name: "Pinecone",        status: "Em breve",     desc: "Vector DB serverless gerenciado" },
  { name: "Weaviate",        status: "Em breve",     desc: "Vector DB open-source" },
];

export default function VectorDBPage() {
  return (
    <section className="space-y-6">
      <header className="flex items-center gap-3">
        <Database size={22} className="text-sky-400" />
        <div>
          <p className="text-xs uppercase tracking-widest text-slate-400">Infrastructure</p>
          <h1 className="text-2xl font-semibold">Vector Database</h1>
          <p className="mt-1 text-sm text-slate-400">Configure o backend de embeddings para RAG</p>
        </div>
      </header>
      <div className="grid gap-4 sm:grid-cols-3">
        {PROVIDERS.map((p) => (
          <article key={p.name} className="rounded-xl border border-slate-800 bg-slate-900/70 p-5 space-y-2">
            <div className="flex items-center justify-between gap-2">
              <h3 className="font-semibold text-slate-100">{p.name}</h3>
              <span className={`rounded-full px-2 py-0.5 text-xs ${p.status === "Configurável" ? "bg-emerald-500/20 text-emerald-400" : "bg-slate-700 text-slate-400"}`}>
                {p.status}
              </span>
            </div>
            <p className="text-sm text-slate-400">{p.desc}</p>
          </article>
        ))}
      </div>
      <p className="text-xs text-slate-500">Configure via variável de ambiente <code className="rounded bg-slate-800 px-1">VECTOR_STORE_URL</code> no backend.</p>
    </section>
  );
}
