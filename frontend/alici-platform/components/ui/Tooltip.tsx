import type { ReactNode } from "react";

interface TooltipProps {
  text: string;
  children: ReactNode;
}

export function Tooltip({ text, children }: TooltipProps) {
  return (
    <span className="group relative inline-flex">
      {children}
      <span className="pointer-events-none absolute -top-10 left-1/2 hidden -translate-x-1/2 rounded-md bg-slate-900 px-2 py-1 text-xs text-slate-100 group-hover:block">
        {text}
      </span>
    </span>
  );
}
