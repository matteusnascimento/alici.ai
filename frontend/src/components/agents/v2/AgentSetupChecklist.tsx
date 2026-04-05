import type { AgentSetupChecklistItem as AgentSetupChecklistItemType } from '../../../types/agentsV2';
import { AgentChecklistItem } from './AgentChecklistItem';

interface AgentSetupChecklistProps {
  items: AgentSetupChecklistItemType[];
}

export function AgentSetupChecklist({ items }: AgentSetupChecklistProps) {
  return (
    <section id="onboarding" className="rounded-3xl border border-white/10 bg-white/5 p-4">
      <h3 className="font-display text-2xl text-white">Checklist de onboarding</h3>
      <div className="mt-3 grid gap-3 lg:grid-cols-2">
        {items.map((item) => (
          <AgentChecklistItem key={item.key} item={item} />
        ))}
      </div>
    </section>
  );
}
