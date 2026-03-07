import type { InputHTMLAttributes } from "react";

type InputProps = InputHTMLAttributes<HTMLInputElement>;

export function Input({ className = "", ...props }: InputProps) {
  return (
    <input
      className={[
        "w-full rounded-lg border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-100",
        "placeholder:text-slate-400 focus:border-sky-400 focus:outline-none",
        className
      ].join(" ")}
      {...props}
    />
  );
}
