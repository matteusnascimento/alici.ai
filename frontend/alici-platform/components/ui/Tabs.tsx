import type { ReactNode } from "react";

interface TabItem {
  key: string;
  label: string;
}

interface TabsProps {
  items: TabItem[];
  active: string;
  onChange: (key: string) => void;
  children?: ReactNode;
}

export function Tabs({ items, active, onChange, children }: TabsProps) {
  return (
    <div>
      <div className="mb-4 flex flex-wrap gap-2">
        {items.map((item) => (
          <button
            key={item.key}
            type="button"
            onClick={() => onChange(item.key)}
            className={[
              "rounded-lg px-3 py-1.5 text-sm",
              item.key === active
                ? "bg-sky-500 text-white"
                : "border border-slate-700 text-slate-300 hover:bg-slate-800"
            ].join(" ")}
          >
            {item.label}
          </button>
        ))}
      </div>
      {children}
    </div>
  );
}
