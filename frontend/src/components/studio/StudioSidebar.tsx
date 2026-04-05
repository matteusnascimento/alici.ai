import { NavLink } from 'react-router-dom';

import { studioNavItems } from './studioConfig';

export function StudioSidebar() {
  return (
    <aside className="rounded-3xl border border-white/10 bg-white/[0.03] p-3 xl:sticky xl:top-6 xl:h-[calc(100vh-8rem)] xl:overflow-auto">
      <p className="mb-3 px-2 text-xs uppercase tracking-[0.25em] text-cyan">AXI Studio</p>
      <nav className="grid gap-2">
        {studioNavItems.map((item) => (
          <NavLink
            key={item.route}
            to={item.route}
            className={({ isActive }) =>
              [
                'group relative flex min-h-[52px] items-center gap-3 overflow-hidden rounded-2xl border px-3 py-2.5 text-sm transition',
                isActive
                  ? 'border-cyan/45 bg-cyan/10 text-white shadow-[inset_0_0_0_1px_rgba(34,211,238,0.12)]'
                  : 'border-transparent bg-white/[0.02] text-slate-300 hover:border-white/10 hover:bg-white/[0.06] hover:text-white',
              ].join(' ')
            }
          >
            <span className="inline-flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-white/10 bg-ink/60 text-cyan">
              <item.icon size={16} />
            </span>
            <span className="min-w-0 truncate font-medium leading-5">{item.title}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
