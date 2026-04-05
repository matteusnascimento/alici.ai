import { Link, useLocation } from 'react-router-dom';

import { studioNavItems, studioSections } from './studioNavigation';

export function StudioSidebar() {
  const location = useLocation();

  return (
    <aside className="h-full overflow-auto rounded-3xl border border-white/10 bg-[linear-gradient(160deg,rgba(6,10,24,0.95),rgba(11,25,46,0.9))] p-3">
      <div className="mb-3 flex items-center justify-between px-2">
        <p className="text-xs uppercase tracking-[0.28em] text-cyan-300">Ferramentas</p>
      </div>
      <div className="space-y-4">
        {studioSections.map((section) => (
          <section key={section.key}>
            <p className="px-2 pb-2 text-[11px] uppercase tracking-[0.18em] text-slate-400">{section.label}</p>
            <div className="space-y-1">
              {studioNavItems.filter((item) => item.section === section.key).map((item) => {
                const active = location.pathname === item.route;
                return (
                  <Link
                    key={`${section.key}-${item.key}`}
                    to={item.route}
                    className={`block rounded-xl px-3 py-2 text-sm transition ${active ? 'bg-cyan/20 text-cyan-100' : 'text-slate-300 hover:bg-white/5 hover:text-white'}`}
                  >
                    {item.label}
                  </Link>
                );
              })}
            </div>
          </section>
        ))}
      </div>
    </aside>
  );
}
