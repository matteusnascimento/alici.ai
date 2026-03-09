import Link from "next/link";
import { Bell, Search, UserCircle2 } from "lucide-react";

export function Topbar() {
  return (
    <header className="flex items-center justify-between border-b border-slate-800 bg-slate-950/60 px-6 py-4">
      <div className="min-w-0">
        <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Workspace</p>
        <h1 className="text-lg font-semibold">ALICI Operations</h1>
      </div>

      <div className="mx-6 hidden max-w-md flex-1 items-center gap-2 rounded-lg border border-slate-800 bg-slate-900/60 px-3 py-2 lg:flex">
        <Search size={16} className="text-slate-400" />
        <input
          type="text"
          placeholder="Search AI"
          className="w-full bg-transparent text-sm text-slate-200 outline-none placeholder:text-slate-500"
        />
      </div>

      <div className="flex items-center gap-2">
        <button
          type="button"
          aria-label="Notifications"
          className="rounded-lg p-2 text-slate-300 transition hover:bg-slate-800"
        >
          <Bell size={18} />
        </button>
        <button
          type="button"
          aria-label="User menu"
          className="rounded-lg p-2 text-slate-300 transition hover:bg-slate-800"
        >
          <UserCircle2 size={20} />
        </button>
        <Link
          href="/agents/create"
          className="rounded-lg bg-sky-500 px-4 py-2 text-sm font-medium text-white hover:bg-sky-400"
        >
          New Agent
        </Link>
      </div>
    </header>
  );
}
