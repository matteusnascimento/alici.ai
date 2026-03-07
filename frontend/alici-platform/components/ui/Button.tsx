import type { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "ghost";
}

export function Button({ variant = "primary", className = "", ...props }: ButtonProps) {
  const base = "rounded-lg px-4 py-2 text-sm font-semibold transition";
  const styles =
    variant === "primary"
      ? "bg-sky-500 text-white hover:bg-sky-400"
      : "border border-slate-700 text-slate-200 hover:bg-slate-800";

  return <button className={`${base} ${styles} ${className}`.trim()} {...props} />;
}
