import { apiFetch } from './api';
import type { AccountActionResponse, AccountChangePasswordPayload, AccountSecuritySummary } from '../types/account';

export function getSecuritySummary() {
  return apiFetch<AccountSecuritySummary>('/account/security');
}

export function changePassword(payload: AccountChangePasswordPayload) {
  return apiFetch<AccountActionResponse>('/account/security/change-password', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
