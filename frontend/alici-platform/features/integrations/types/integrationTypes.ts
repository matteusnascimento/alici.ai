export interface IntegrationItem {
  id: string;
  provider: string;
  status: "connected" | "disconnected";
  lastSync: string;
}

export interface IntegrationListResponse {
  integrations: IntegrationItem[];
}
