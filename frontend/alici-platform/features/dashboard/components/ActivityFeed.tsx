import type { ActivityItem } from "@/types/dashboard";

interface ActivityFeedProps {
  activity: ActivityItem[];
}

export function ActivityFeed({ activity }: ActivityFeedProps) {
  return (
    <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-5">
      <h3 className="text-sm font-semibold text-slate-200">Activity Feed</h3>
      <ul className="mt-4 space-y-3">
        {activity.map((event) => (
          <li key={event.id} className="rounded-lg border border-slate-800 px-4 py-3">
            <p className="text-sm text-slate-100">{event.description}</p>
            <p className="mt-1 text-xs text-slate-400">{event.timestamp}</p>
          </li>
        ))}
      </ul>
    </section>
  );
}
