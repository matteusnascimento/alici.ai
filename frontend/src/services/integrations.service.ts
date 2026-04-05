import { apiFetch } from './api';
import type { AccountIntegration } from '../types/account';

export function getAccountIntegrations() {
  return apiFetch<AccountIntegration[]>('/account/integrations');
}

export function setIntegrationStatus(provider: string, enabled: boolean) {
  return apiFetch<AccountIntegration>(`/account/integrations/${provider}`, {
    method: 'PUT',
    body: JSON.stringify({ enabled }),
  });
}
