"use client";

import { useWorkflows } from "../hooks/useWorkflows";

export function WorkflowsPage() {
  const { loading, workflows } = useWorkflows();

  if (loading) {
    return <div className="text-sm text-slate-300">Loading workflows...</div>;
  }

  return (
    <section className="space-y-4">
      <div>
        <p className="text-xs uppercase tracking-widest text-slate-400">Workflows</p>
        <h2 className="text-2xl font-semibold">Automation Engine</h2>
      </div>
      <div className="overflow-x-auto rounded-xl border border-slate-800">
        <table className="min-w-full border-collapse">
          <thead>
            <tr className="bg-slate-900/70">
              <th className="px-4 py-3 text-left text-xs uppercase tracking-wider text-slate-400">Name</th>
              <th className="px-4 py-3 text-left text-xs uppercase tracking-wider text-slate-400">Trigger</th>
              <th className="px-4 py-3 text-left text-xs uppercase tracking-wider text-slate-400">Runs Today</th>
              <th className="px-4 py-3 text-left text-xs uppercase tracking-wider text-slate-400">Success Rate</th>
            </tr>
          </thead>
          <tbody>
            {workflows.map((workflow) => (
              <tr key={workflow.id} className="border-t border-slate-800">
                <td className="px-4 py-3 text-sm text-slate-100">{workflow.name}</td>
                <td className="px-4 py-3 text-sm text-slate-300">{workflow.trigger}</td>
                <td className="px-4 py-3 text-sm text-slate-300">{workflow.runsToday}</td>
                <td className="px-4 py-3 text-sm text-emerald-300">{workflow.successRate}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
