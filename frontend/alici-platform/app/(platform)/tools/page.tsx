"use client";

import { Globe, Code, FileText, Database, Wrench } from "lucide-react";

const TOOLS = [
  { id: "web_search",       icon: Globe,     label: "Web Search",       desc: "Busca em tempo real via DuckDuckGo", status: "active" },
  { id: "code_interpreter", icon: Code,      label: "Code Interpreter",  desc: "Execução e depuração de código Python/JS", status: "active" },
  { id: "file_reader",      icon: FileText,  label: "File Reader",       desc: "Leitura e parsing de PDF, DOCX, CSV, TXT", status: "active" },
  { id: "database_query",   icon: Database,  label: "Database Query",    desc: "Consulta em fontes de dados conectadas", status: "soon" },
];

export default function ToolsPage() {
  return (
    <section className="space-y-6">
      <header className="flex items-center gap-3">
        <Wrench size={22} className="text-sky-400" />
        <div>
          <p className="text-xs uppercase tracking-widest text-slate-400">Platform</p>
          <h1 className="text-2xl font-semibold">Tools</h1>
          <p className="mt-1 text-sm text-slate-400">Ferramentas disponíveis para seus agentes</p>
        </div>
      </header>
      <div className="grid gap-4 sm:grid-cols-2">
        {TOOLS.map((tool) => {
          const Icon = tool.icon;
          return (
            <article key={tool.id}
              className="rounded-xl border border-slate-800 bg-slate-900/70 p-5 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Icon size={18} className="text-sky-400" />
                  <h3 className="font-semibold text-slate-100">{tool.label}</h3>
                </div>
                {tool.status === "active"
                  ? <span className="rounded-full bg-emerald-500/20 px-2 py-0.5 text-xs text-emerald-400">Ativo</span>
                  : <span className="rounded-full bg-slate-700 px-2 py-0.5 text-xs text-slate-400">Em breve</span>}
              </div>
              <p className="text-sm text-slate-400">{tool.desc}</p>
            </article>
          );
        })}
      </div>
    </section>
  );
}
