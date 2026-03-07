"use client";

import { create } from "zustand";
import type { WorkflowItem } from "../types/workflowTypes";

interface WorkflowState {
  loading: boolean;
  workflows: WorkflowItem[];
  setWorkflows: (workflows: WorkflowItem[]) => void;
}

export const useWorkflowStore = create<WorkflowState>((set) => ({
  loading: true,
  workflows: [],
  setWorkflows: (workflows) => set({ workflows, loading: false })
}));
