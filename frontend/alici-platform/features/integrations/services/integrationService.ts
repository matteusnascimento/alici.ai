import { api } from "@/services/api";
import type { IntegrationListResponse } from "../types/integrationTypes";

const fallback: IntegrationListResponse = {
  integrations: [
    { id: "int-01", provider: "Slack", status: "connected", lastSync: "2 min ago" },
    { id: "int-02", provider: "WhatsApp", status: "connected", lastSync: "5 min ago" },
    { id: "int-03", provider: "Discord", status: "disconnected", lastSync: "never" }
  ]
};

export async function fetchIntegrations(): Promise<IntegrationListResponse> {
  try {
    const response = await api.get<IntegrationListResponse>("/integrations");
    return response.data;
  } catch {
    return fallback;
  }
}
