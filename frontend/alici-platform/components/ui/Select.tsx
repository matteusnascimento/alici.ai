import type { SelectHTMLAttributes } from "react";

type SelectProps = SelectHTMLAttributes<HTMLSelectElement>;

export function Select({ className = "", children, ...props }: SelectProps) {
  return (
    <select
      className={[
        "w-full rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-100",
        "focus:border-sky-400 focus:outline-none",
        className
      ].join(" ")}
      {...props}
    >
      {children}
    </select>
  );
}
