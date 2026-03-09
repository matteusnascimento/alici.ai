"use client";

import { useEffect } from "react";
import { useState } from "react";
import { fetchAgents } from "@/features/agents/services/agentService";
import { useAgentStore } from "@/features/agents/store/agentStore";

export function useAgents() {
  const { agents, setAgents } = useAgentStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchAgents();
        if (active) setAgents(data.agents);
      } catch {
        if (active) setError("Failed to load agents");
      } finally {
        if (active) setLoading(false);
      }
    }

    void load();
    return () => {
      active = false;
    };
  }, [setAgents]);

  return { loading, error, data: agents, agents };
}
