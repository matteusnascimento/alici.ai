import { Link } from 'react-router-dom';

import type { AgentSetupChecklistItem } from '../../../types/agentsV2';

interface AgentChecklistItemProps {
  item: AgentSetupChecklistItem;
}

export function AgentChecklistItem({ item }: AgentChecklistItemProps) {
  return (
    <Link to={item.route} className="block rounded-2xl border border-white/10 bg-white/5 p-3 transition hover:border-cyan-300/40">
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-sm font-semibold text-white">{item.label}</p>
          <p className="mt-1 text-xs text-slate-300">{item.detail}</p>
          {item.helper_text ? <p className="mt-1 text-xs text-slate-400">{item.helper_text}</p> : null}
        </div>
        <span className={`rounded-full px-2 py-1 text-xs font-semibold ${item.completed ? 'bg-emerald-500/15 text-emerald-200' : 'bg-amber-500/15 text-amber-100'}`}>
          {item.completed ? 'Concluido' : 'Pendente'}
        </span>
      </div>
    </Link>
  );
}
