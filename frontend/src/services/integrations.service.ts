import { apiFetch } from './api';
import type { AccountIntegration } from '../types/account';

export interface IntegrationProvider {
  provider: string;
  title: string;
  description: string;
  status: string;
  helper_text: string;
  connected_accounts: number;
  active_bindings: number;
  supports_activation: boolean;
}

export interface IntegrationAccount {
  id: number;
  provider: string;
  external_account_id?: string | null;
  external_account_name?: string | null;
  status: string;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface IntegrationProviderStatus {
  provider: string;
  status: string;
  connected_accounts: number;
  active_endpoints: number;
  active_bindings: number;
  helper_text: string;
}

// Account-level integrations (AI providers, OpenAI key, etc.)
export function getAccountIntegrations() {
  return apiFetch<AccountIntegration[]>('/account/integrations');
}

export function setIntegrationStatus(provider: string, enabled: boolean) {
  return apiFetch<AccountIntegration>(`/account/integrations/${provider}`, {
    method: 'PUT',
    body: JSON.stringify({ enabled }),
  });
}

// Channel integrations (WhatsApp, Instagram, etc.)
export function listChannelIntegrations(): Promise<IntegrationProvider[]> {
  return apiFetch<IntegrationProvider[]>('/integrations');
}

export function listIntegrationAccounts(): Promise<IntegrationAccount[]> {
  return apiFetch<IntegrationAccount[]>('/integrations/accounts');
}

export function connectIntegration(payload: {
  provider: string;
  external_account_id?: string;
  external_account_name?: string;
  access_token?: string;
  metadata?: Record<string, unknown>;
}): Promise<IntegrationAccount> {
  return apiFetch<IntegrationAccount>('/integrations', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function startIntegrationOAuth(provider: string): Promise<{ provider: string; authorization_url: string }> {
  return apiFetch<{ provider: string; authorization_url: string }>(`/integrations/${provider}/oauth/start`, {
    method: 'POST',
  });
}

export function getProviderStatus(provider: string): Promise<IntegrationProviderStatus> {
  return apiFetch<IntegrationProviderStatus>(`/integrations/${provider}/status`);
}

export function disconnectProvider(provider: string): Promise<IntegrationProviderStatus> {
  return apiFetch<IntegrationProviderStatus>(`/integrations/${provider}/disconnect`, { method: 'POST' });
}
