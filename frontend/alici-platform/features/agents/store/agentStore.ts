"use client";

import { create } from "zustand";
import type { AgentItem } from "../types/agentTypes";

interface AgentState {
  loading: boolean;
  agents: AgentItem[];
  setAgents: (agents: AgentItem[]) => void;
}

export const useAgentStore = create<AgentState>((set) => ({
  loading: true,
  agents: [],
  setAgents: (agents) => set({ agents, loading: false })
}));
