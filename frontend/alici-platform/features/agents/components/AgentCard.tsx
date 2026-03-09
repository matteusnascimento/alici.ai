"use client";

import Link from "next/link";
import { Pencil, Trash2 } from "lucide-react";
import { useState } from "react";
import type { AgentItem } from "../types/agentTypes";
import { Badge } from "@/components/ui/Badge";

interface AgentCardProps {
  agent: AgentItem;
  onDelete?: (agentId: string) => Promise<void>;
}

export function AgentCard({ agent, onDelete }: AgentCardProps) {
  const [deleting, setDeleting] = useState(false);

  async function handleDelete() {
    if (!onDelete || deleting) return;
    setDeleting(true);
    try {
      await onDelete(agent.id);
    } finally {
      setDeleting(false);
    }
  }

  return (
    <article className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-100">{agent.name}</h3>
        <Badge tone={agent.status === "online" ? "success" : "warning"}>{agent.status}</Badge>
      </div>
      {agent.description && (
        <p className="text-xs text-slate-400 line-clamp-2">{agent.description}</p>
      )}
      <p className="text-xs text-slate-400">Model: {agent.model}</p>
      <p className="text-xs text-slate-300">Requests today: {agent.requestsToday}</p>

      <div className="flex items-center gap-2 mt-auto pt-2 border-t border-slate-800">
        <Link
          href={`/agents/${agent.id}`}
          className="flex flex-1 items-center justify-center gap-1.5 rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-200 transition hover:bg-slate-800"
        >
          <Pencil size={12} />
          Edit
        </Link>
        <button
          type="button"
          onClick={() => void handleDelete()}
          disabled={deleting}
          className="flex flex-1 items-center justify-center gap-1.5 rounded-lg border border-red-900/50 px-3 py-1.5 text-xs font-medium text-red-400 transition hover:bg-red-500/10 disabled:opacity-50"
        >
          <Trash2 size={12} />
          {deleting ? "Deleting..." : "Delete"}
        </button>
      </div>
    </article>
  );
}
