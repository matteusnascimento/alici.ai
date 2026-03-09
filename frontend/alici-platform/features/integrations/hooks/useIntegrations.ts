"use client";

import { useEffect } from "react";
import { useState } from "react";
import { fetchIntegrations } from "@/features/integrations/services/integrationService";
import { useIntegrationStore } from "@/features/integrations/store/integrationStore";

export function useIntegrations() {
  const { integrations, setIntegrations } = useIntegrationStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchIntegrations();
        if (active) setIntegrations(data.integrations);
      } catch {
        if (active) setError("Failed to load integrations");
      } finally {
        if (active) setLoading(false);
      }
    }

    void load();
    return () => {
      active = false;
    };
  }, [setIntegrations]);

  return { loading, error, data: integrations, integrations };
}
