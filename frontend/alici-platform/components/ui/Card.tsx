import type { ReactNode } from "react";

export function Card({ children }: { children: ReactNode }) {
  return <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">{children}</div>;
}
