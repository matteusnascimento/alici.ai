import type { ReactNode } from "react";

interface DropdownOption {
  key: string;
  label: string;
}

interface DropdownProps {
  title: string;
  options: DropdownOption[];
  onSelect: (key: string) => void;
  footer?: ReactNode;
}

export function Dropdown({ title, options, onSelect, footer }: DropdownProps) {
  return (
    <div className="w-64 rounded-xl border border-slate-800 bg-slate-900/95 p-2 shadow-lg">
      <p className="px-2 py-1 text-xs uppercase tracking-wide text-slate-400">{title}</p>
      <div className="mt-1 space-y-1">
        {options.map((option) => (
          <button
            key={option.key}
            type="button"
            className="w-full rounded-lg px-3 py-2 text-left text-sm text-slate-200 hover:bg-slate-800"
            onClick={() => onSelect(option.key)}
          >
            {option.label}
          </button>
        ))}
      </div>
      {footer ? <div className="mt-2 border-t border-slate-800 px-2 pt-2">{footer}</div> : null}
    </div>
  );
}
