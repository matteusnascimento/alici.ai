import { apiFetch } from './api';
import type {
  BillingPlan,
  BillingUsage,
  CurrentSubscription,
  UpgradePayload,
  UpgradeResponse,
} from '../types/billing';

export function getBillingPlans() {
  return apiFetch<BillingPlan[]>('/billing/plans');
}

export function getCurrentSubscription() {
  return apiFetch<CurrentSubscription>('/billing/current');
}

export function upgradeSubscription(payload: UpgradePayload) {
  return apiFetch<UpgradeResponse>('/billing/upgrade', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getBillingUsage() {
  return apiFetch<BillingUsage>('/billing/usage');
}
