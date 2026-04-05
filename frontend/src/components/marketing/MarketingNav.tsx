import {
  BarChart3,
  ClipboardList,
  FileStack,
  Image,
  LayoutTemplate,
  MessageCircleMore,
  NotepadText,
  Orbit,
  Rocket,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

import type { MarketingSectionId } from '../../types/marketing';

const items: Array<{ id: MarketingSectionId; label: string; icon: LucideIcon }> = [
  { id: 'campaigns', label: 'Campaigns', icon: Rocket },
  { id: 'creatives', label: 'Creatives', icon: Image },
  { id: 'content-planner', label: 'Content Planner', icon: ClipboardList },
  { id: 'posts-copy', label: 'Posts & Copy', icon: NotepadText },
  { id: 'funnels', label: 'Funnels', icon: Orbit },
  { id: 'whatsapp', label: 'WhatsApp', icon: MessageCircleMore },
  { id: 'landing-pages', label: 'Landing Pages', icon: FileStack },
  { id: 'templates', label: 'Templates', icon: LayoutTemplate },
  { id: 'analytics', label: 'Analytics', icon: BarChart3 },
];

interface MarketingNavProps {
  active: MarketingSectionId;
  onChange: (next: MarketingSectionId) => void;
}

export function MarketingNav({ active, onChange }: MarketingNavProps) {
  return (
    <nav className="sticky top-4 z-10 rounded-3xl border border-white/10 bg-storm/70 p-3 backdrop-blur">
      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-1">
        {items.map((item) => {
          const isActive = active === item.id;
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => onChange(item.id)}
              className={[
                'group flex w-full items-center gap-3 rounded-2xl px-3 py-3 text-left text-sm transition',
                isActive
                  ? 'border border-cyan/40 bg-cyan/10 text-white'
                  : 'border border-transparent bg-white/[0.03] text-slate-300 hover:border-white/10 hover:bg-white/[0.06]',
              ].join(' ')}
            >
              <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-ink/60 text-cyan">
                <item.icon size={16} />
              </span>
              <span className="font-medium">{item.label}</span>
            </button>
          );
        })}
      </div>
    </nav>
  );
}
