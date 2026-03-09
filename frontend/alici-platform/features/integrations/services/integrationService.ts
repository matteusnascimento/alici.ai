import { api } from "@/services/api";
import type { ApiEnvelope } from "@/types/api";
import type { IntegrationListResponse } from "../types/integrationTypes";

const fallback: IntegrationListResponse = {
  integrations: [
    { id: "int-01", provider: "Slack", status: "connected", lastSync: "2 min ago" },
    { id: "int-02", provider: "WhatsApp", status: "connected", lastSync: "5 min ago" },
    { id: "int-03", provider: "Discord", status: "disconnected", lastSync: "never" }
  ]
};

export async function fetchIntegrations(): Promise<IntegrationListResponse> {
  /**
   * Function: fetchIntegrations
   * Description: Fetch organization integrations using the standard API envelope.
   * Parameters:
   * Returns:
   *   IntegrationListResponse with normalized items.
   */
  try {
    const response = await api.get<ApiEnvelope<IntegrationListResponse>>("/integrations");
    const envelopeData = response.data?.data ?? fallback;
    return {
      integrations: (envelopeData.integrations || []).map((item) => ({
        ...item,
        status: item.status === "connected" ? "connected" : "disconnected"
      }))
    };
  } catch {
    return fallback;
  }
}
