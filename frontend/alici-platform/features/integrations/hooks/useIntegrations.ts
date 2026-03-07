"use client";

import { useEffect } from "react";
import { fetchIntegrations } from "../services/integrationService";
import { useIntegrationStore } from "../store/integrationStore";

export function useIntegrations() {
  const { loading, integrations, setIntegrations } = useIntegrationStore();

  useEffect(() => {
    async function load() {
      const data = await fetchIntegrations();
      setIntegrations(data.integrations);
    }

    void load();
  }, [setIntegrations]);

  return { loading, integrations };
}
