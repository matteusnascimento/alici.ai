import { apiFetch } from './api';
import type { AccountData, Profile, UserSettings } from '../types/settings';

export function getAccountData() {
  return apiFetch<AccountData>('/settings/me');
}

export function updateProfile(payload: Profile) {
  return apiFetch<Profile>('/settings/profile', {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

export function updateSettings(payload: UserSettings) {
  return apiFetch<UserSettings>('/settings/me', {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}
