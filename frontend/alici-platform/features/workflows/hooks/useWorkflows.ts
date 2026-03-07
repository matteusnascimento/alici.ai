"use client";

import { useEffect } from "react";
import { fetchWorkflows } from "../services/workflowService";
import { useWorkflowStore } from "../store/workflowStore";

export function useWorkflows() {
  const { loading, workflows, setWorkflows } = useWorkflowStore();

  useEffect(() => {
    async function load() {
      const data = await fetchWorkflows();
      setWorkflows(data.workflows);
    }

    void load();
  }, [setWorkflows]);

  return { loading, workflows };
}
