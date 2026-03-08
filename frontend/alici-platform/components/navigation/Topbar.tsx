import Link from "next/link";

export function Topbar() {
  return (
    <header className="flex items-center justify-between border-b border-slate-800 bg-slate-950/60 px-6 py-4">
      <div>
        <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Workspace</p>
        <h1 className="text-lg font-semibold">ALICI Operations</h1>
      </div>
      <Link
        href="/agents/create"
        className="rounded-lg bg-sky-500 px-4 py-2 text-sm font-medium text-white hover:bg-sky-400"
      >
        New Agent
      </Link>
    </header>
  );
}
