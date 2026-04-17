import { apiFetch } from './api';
import type {
  BillingHistory,
  BillingPlan,
  BillingUsage,
  CheckoutPayload,
  CheckoutResponse,
  CurrentSubscription,
  PortalResponse,
  SubscriptionActionResponse,
  UpgradePayload,
  UpgradeResponse,
} from '../types/billing';

export function getBillingPlans() {
  return apiFetch<BillingPlan[]>('/billing/plans');
}

export function getCurrentSubscription() {
  return apiFetch<CurrentSubscription>('/billing/current');
}

/** @deprecated Fluxo administrativo/legado. Use createCheckoutSession() para fluxo real. */
export function upgradeSubscription(payload: UpgradePayload) {
  return apiFetch<UpgradeResponse>('/billing/upgrade', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getBillingUsage() {
  return apiFetch<BillingUsage>('/billing/usage');
}

// ── Stripe real ──────────────────────────────────────────────────────

export function createCheckoutSession(payload: CheckoutPayload) {
  return apiFetch<CheckoutResponse>('/billing/checkout', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function createPortalSession() {
  return apiFetch<PortalResponse>('/billing/portal', { method: 'POST' });
}

export function cancelSubscription() {
  return apiFetch<SubscriptionActionResponse>('/billing/cancel', { method: 'POST' });
}

export function resumeSubscription() {
  return apiFetch<SubscriptionActionResponse>('/billing/resume', { method: 'POST' });
}

export function getBillingHistory() {
  return apiFetch<BillingHistory>('/billing/history');
}
