import type { ReactNode } from "react";

interface BadgeProps {
  children: ReactNode;
  tone?: "neutral" | "success" | "warning" | "danger";
}

const toneClasses: Record<NonNullable<BadgeProps["tone"]>, string> = {
  neutral: "bg-slate-800 text-slate-200",
  success: "bg-emerald-500/20 text-emerald-300",
  warning: "bg-amber-500/20 text-amber-300",
  danger: "bg-rose-500/20 text-rose-300"
};

export function Badge({ children, tone = "neutral" }: BadgeProps) {
  return (
    <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${toneClasses[tone]}`}>
      {children}
    </span>
  );
}
