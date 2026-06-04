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
  account_name?: string | null;
  last_sync_at?: string | null;
  last_error?: string | null;
  data_received?: number | null;
  scopes?: string[];
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
  account_name?: string | null;
  last_sync_at?: string | null;
  last_error?: string | null;
  data_received?: number | null;
  scopes?: string[];
}

export interface IntegrationOAuthStartResponse {
  provider: string;
  authorization_url: string;
}

export interface IntegrationQrStartResponse {
  provider: string;
  qr_code_url: string;
  pairing_code: string;
  expires_at: string;
}

export interface WebsiteChatScriptResponse {
  provider: string;
  company_id: string;
  script: string;
}

export interface ProviderCredentialPayload {
  endpoint?: string;
  api_key?: string;
  token?: string;
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

export function connectProvider(provider: string, payload: {
  external_account_id?: string;
  external_account_name?: string;
  access_token?: string;
  metadata?: Record<string, unknown>;
}): Promise<IntegrationAccount> {
  return apiFetch<IntegrationAccount>(`/integrations/${provider}/connect`, {
    method: 'POST',
    body: JSON.stringify({ provider, ...payload }),
  });
}

export function startIntegrationOAuth(provider: string, redirectPath?: string): Promise<IntegrationOAuthStartResponse> {
  return apiFetch<IntegrationOAuthStartResponse>(`/integrations/${provider}/oauth/start`, {
    method: 'POST',
    body: JSON.stringify({ redirect_path: redirectPath }),
  });
}

export function startMetaOAuth(provider: string): Promise<IntegrationOAuthStartResponse> {
  return apiFetch<IntegrationOAuthStartResponse>(`/integrations/meta/connect?provider=${encodeURIComponent(provider)}`);
}

export function startGoogleOAuth(provider: string): Promise<IntegrationOAuthStartResponse> {
  return apiFetch<IntegrationOAuthStartResponse>(`/integrations/google/connect?provider=${encodeURIComponent(provider)}`);
}

export function startWhatsAppQr(redirectPath?: string): Promise<IntegrationQrStartResponse> {
  return apiFetch<IntegrationQrStartResponse>('/integrations/whatsapp/qr/start', {
    method: 'POST',
    body: JSON.stringify({ redirect_path: redirectPath }),
  });
}

export function getProviderStatus(provider: string): Promise<IntegrationProviderStatus> {
  return apiFetch<IntegrationProviderStatus>(`/integrations/${provider}/status`);
}

export function testProviderCredentials(provider: string, payload: ProviderCredentialPayload): Promise<{
  provider: string;
  status: string;
  message: string;
  status_code?: number | null;
}> {
  return apiFetch(`/integrations/${provider}/test`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function connectProviderCredentials(provider: string, payload: ProviderCredentialPayload): Promise<IntegrationAccount> {
  return apiFetch<IntegrationAccount>(`/integrations/${provider}/connect`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getWebsiteChatScript(): Promise<WebsiteChatScriptResponse> {
  return apiFetch<WebsiteChatScriptResponse>('/integrations/website-chat/widget-script');
}

export function testWebsiteChatInstallation(companyId: string): Promise<{
  provider: string;
  status: string;
  message: string;
  status_code?: number | null;
}> {
  return apiFetch('/integrations/website-chat/test-installation', {
    method: 'POST',
    body: JSON.stringify({ endpoint: companyId }),
  });
}

export function disconnectProvider(provider: string): Promise<IntegrationProviderStatus> {
  return apiFetch<IntegrationProviderStatus>(`/integrations/${provider}/disconnect`, { method: 'POST' });
}

export function testProvider(provider: string): Promise<{
  provider: string;
  status: string;
  message: string;
  status_code?: number | null;
}> {
  return apiFetch(`/integrations/${provider}/test`, {
    method: 'POST',
    body: JSON.stringify({}),
  });
}

export function syncProvider(provider: string): Promise<{
  provider: string;
  status: string;
  message: string;
  status_code?: number | null;
}> {
  return apiFetch(`/integrations/${provider}/sync`, {
    method: 'POST',
    body: JSON.stringify({}),
  });
}
