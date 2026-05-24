import { Link } from 'react-router-dom';

import type { AgentSetupChecklistItem } from '../../../types/agentsV2';

interface AgentQuickNavigationCardsProps {
  items: AgentSetupChecklistItem[];
}

export function AgentQuickNavigationCards({ items }: AgentQuickNavigationCardsProps) {
  return (
    <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
      {items.map((item) => (
        <Link key={item.key} to={item.route} className="rounded-2xl border border-white/10 bg-white/5 p-3 transition hover:border-cyan-300/35">
          <p className="text-sm font-semibold text-white">{item.label}</p>
          <p className="mt-1 text-xs text-slate-300">{item.detail}</p>
          <p className={`mt-2 text-xs font-semibold ${item.completed ? 'text-emerald-200' : 'text-amber-100'}`}>
            {item.completed ? 'Pronto' : 'Pendente'}
          </p>
        </Link>
      ))}
    </section>
  );
}
