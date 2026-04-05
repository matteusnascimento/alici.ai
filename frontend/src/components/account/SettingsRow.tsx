import { ChevronRight } from 'lucide-react';
import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';

interface SettingsRowProps {
  label: string;
  description: string;
  to?: string;
  action?: ReactNode;
}

export function SettingsRow({ label, description, to, action }: SettingsRowProps) {
  const content = (
    <div className="flex w-full items-center justify-between rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3">
      <div>
        <p className="text-sm font-medium text-white">{label}</p>
        <p className="text-xs text-slate-300">{description}</p>
      </div>
      <div className="flex items-center gap-2 text-slate-300">
        {action}
        {to ? <ChevronRight size={16} /> : null}
      </div>
    </div>
  );

  if (to) {
    return <Link to={to}>{content}</Link>;
  }
  return content;
}
