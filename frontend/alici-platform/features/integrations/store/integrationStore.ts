"use client";

import { create } from "zustand";
import type { IntegrationItem } from "../types/integrationTypes";

interface IntegrationState {
  loading: boolean;
  integrations: IntegrationItem[];
  setIntegrations: (integrations: IntegrationItem[]) => void;
}

export const useIntegrationStore = create<IntegrationState>((set) => ({
  loading: true,
  integrations: [],
  setIntegrations: (integrations) => set({ integrations, loading: false })
}));
