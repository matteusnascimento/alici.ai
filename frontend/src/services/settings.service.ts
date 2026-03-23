import { apiFetch } from './api';
import type { AccountData, Profile, ProfileUpdate, UserSettings } from '../types/settings';

export function getAccountData() {
  return apiFetch<AccountData>('/settings/me');
}

export function updateProfile(payload: ProfileUpdate) {
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
