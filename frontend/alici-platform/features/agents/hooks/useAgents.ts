"use client";

import { useEffect } from "react";
import { fetchAgents } from "../services/agentService";
import { useAgentStore } from "../store/agentStore";

export function useAgents() {
  const { loading, agents, setAgents } = useAgentStore();

  useEffect(() => {
    async function load() {
      const data = await fetchAgents();
      setAgents(data.agents);
    }

    void load();
  }, [setAgents]);

  return { loading, agents };
}
