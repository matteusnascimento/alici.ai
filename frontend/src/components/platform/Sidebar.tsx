import { Bot, ChartColumnBig, LayoutDashboard, Megaphone, Settings2 } from 'lucide-react';
import { NavLink } from 'react-router-dom';

import { cn } from '../../utils/cn';

const items = [
  { label: 'Dashboard', to: '/app/dashboard', icon: LayoutDashboard },
  { label: 'Alici Chat', to: '/app/chat', icon: Bot },
  { label: 'Agents', to: '/app/agents', icon: ChartColumnBig },
  { label: 'AXI Growth Studio', to: '/app/marketing', icon: Megaphone },
  { label: 'Conta AXI', to: '/app/account', icon: Settings2 },
];

export function Sidebar() {
  return (
    <aside className="flex h-full flex-col rounded-[2rem] border border-white/10 bg-storm/70 p-6 backdrop-blur">
      <div>
        <p className="text-sm uppercase tracking-[0.35em] text-cyan">AXI</p>
        <h1 className="mt-4 font-display text-3xl text-white">Control Room</h1>
        <p className="mt-3 text-sm text-slate-300">Operação unificada de chat, agentes e crescimento.</p>
      </div>
      <nav className="mt-10 flex flex-1 flex-col gap-2">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium text-slate-200 transition',
                isActive && 'bg-white/10 text-white',
              )
            }
          >
            <item.icon size={18} />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
