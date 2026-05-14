import { apiFetch } from './api';
import type {
  AccountActionResponse,
  AccountArchivedChatList,
  AccountHelpInfo,
  AccountLegalInfo,
  AccountPrivacy,
  AccountProfile,
  AccountProfileUpdate,
  AccountVerificationChallenge,
  AccountVerificationConfirmPayload,
} from '../types/account';
import type { CurrentSubscription } from '../types/billing';

export function uploadAccountAvatar(file: File) {
  const body = new FormData();
  body.append('file', file);
  return apiFetch<{ avatar_url: string }>('/account/upload-avatar', {
    method: 'POST',
    body,
  });
}

export function getAccountProfile() {
  return apiFetch<AccountProfile>('/account/profile');
}

export function updateAccountProfile(payload: AccountProfileUpdate) {
  return apiFetch<AccountProfile>('/account/profile', {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

export function requestEmailVerification() {
  return apiFetch<AccountVerificationChallenge>('/account/profile/verify-email/request', { method: 'POST' });
}

export function confirmEmailVerification(payload: AccountVerificationConfirmPayload) {
  return apiFetch<AccountActionResponse>('/account/profile/verify-email/confirm', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function requestPhoneVerification() {
  return apiFetch<AccountVerificationChallenge>('/account/profile/verify-phone/request', { method: 'POST' });
}

export function confirmPhoneVerification(payload: AccountVerificationConfirmPayload) {
  return apiFetch<AccountActionResponse>('/account/profile/verify-phone/confirm', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getAccountSubscription() {
  return apiFetch<CurrentSubscription>('/account/subscription');
}

export function getArchivedChats() {
  return apiFetch<AccountArchivedChatList>('/account/chats/archived');
}

export function getPrivacyInfo() {
  return apiFetch<AccountPrivacy>('/account/privacy');
}

export function requestDataExport() {
  return apiFetch<AccountActionResponse>('/account/privacy/export', { method: 'POST' });
}

export function requestAccountDeletion() {
  return apiFetch<AccountActionResponse>('/account/privacy/delete-request', { method: 'POST' });
}

export function getHelpInfo() {
  return apiFetch<AccountHelpInfo>('/account/help');
}

export function getLegalInfo() {
  return apiFetch<AccountLegalInfo>('/account/legal');
}

export function logoutAccount() {
  return apiFetch<AccountActionResponse>('/account/logout', { method: 'POST' });
}
