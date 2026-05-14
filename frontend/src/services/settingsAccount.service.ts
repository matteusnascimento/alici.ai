import { apiFetch } from './api';
import type { AccountNotifications, AccountPreferences } from '../types/account';

export function getAccountPreferences() {
  return apiFetch<AccountPreferences>('/account/preferences');
}

export function updateAccountPreferences(payload: AccountPreferences) {
  return apiFetch<AccountPreferences>('/account/preferences', {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

export function getAccountNotifications() {
  return apiFetch<AccountNotifications>('/account/notifications');
}

export function updateAccountNotifications(payload: AccountNotifications) {
  return apiFetch<AccountNotifications>('/account/notifications', {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}
