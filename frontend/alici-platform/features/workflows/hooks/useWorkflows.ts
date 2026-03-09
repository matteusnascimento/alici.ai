"use client";

import { useEffect } from "react";
import { useState } from "react";
import { fetchWorkflows } from "@/features/workflows/services/workflowService";
import { useWorkflowStore } from "@/features/workflows/store/workflowStore";

export function useWorkflows() {
  const { workflows, setWorkflows } = useWorkflowStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchWorkflows();
        if (active) setWorkflows(data.workflows);
      } catch {
        if (active) setError("Failed to load workflows");
      } finally {
        if (active) setLoading(false);
      }
    }

    void load();
    return () => {
      active = false;
    };
  }, [setWorkflows]);

  return { loading, error, data: workflows, workflows };
}
