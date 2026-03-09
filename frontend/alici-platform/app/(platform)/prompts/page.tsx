import { FileCode } from "lucide-react";

export default function PromptsPage() {
  return (
    <section className="space-y-4">
      <header className="flex items-center gap-3">
        <FileCode size={22} className="text-sky-400" />
        <div>
          <p className="text-xs uppercase tracking-widest text-slate-400">AI Studio</p>
          <h1 className="text-2xl font-semibold">Prompts</h1>
        </div>
      </header>
      <div className="rounded-xl border border-dashed border-slate-700 p-8 text-center">
        <p className="text-sm text-slate-400">Biblioteca de prompts — em desenvolvimento.</p>
        <p className="mt-1 text-xs text-slate-600">Use as Instructions do Agent Builder para criar prompts agora.</p>
      </div>
    </section>
  );
}
