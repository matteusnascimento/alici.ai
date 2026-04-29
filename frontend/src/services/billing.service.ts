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

type ApiEnvelope<T> = {
  status?: string;
  data?: T;
  error?: unknown;
};

function unwrapApiData<T>(value: T | ApiEnvelope<T>): T {
  if (value && typeof value === 'object' && 'data' in value && ('status' in value || 'error' in value)) {
    return (value as ApiEnvelope<T>).data as T;
  }
  return value as T;
}

export function getBillingPlans() {
  return apiFetch<BillingPlan[] | ApiEnvelope<BillingPlan[]>>('/billing/plans').then(unwrapApiData);
}

export function getCurrentSubscription() {
  return apiFetch<CurrentSubscription | ApiEnvelope<CurrentSubscription>>('/billing/current').then(unwrapApiData);
}

/** @deprecated Fluxo administrativo/legado. Use createCheckoutSession() para fluxo real. */
export function upgradeSubscription(payload: UpgradePayload) {
  return apiFetch<UpgradeResponse | ApiEnvelope<UpgradeResponse>>('/billing/upgrade', {
    method: 'POST',
    body: JSON.stringify(payload),
  }).then(unwrapApiData);
}

export function getBillingUsage() {
  return apiFetch<BillingUsage | ApiEnvelope<BillingUsage>>('/billing/usage').then(unwrapApiData);
}

// ── Stripe real ──────────────────────────────────────────────────────

export function createCheckoutSession(payload: CheckoutPayload) {
  return apiFetch<CheckoutResponse | ApiEnvelope<CheckoutResponse>>('/billing/checkout', {
    method: 'POST',
    body: JSON.stringify(payload),
  }).then(unwrapApiData);
}

export function createPortalSession() {
  return apiFetch<PortalResponse | ApiEnvelope<PortalResponse>>('/billing/portal', { method: 'POST' }).then(unwrapApiData);
}

export function cancelSubscription() {
  return apiFetch<SubscriptionActionResponse | ApiEnvelope<SubscriptionActionResponse>>('/billing/cancel', { method: 'POST' }).then(unwrapApiData);
}

export function resumeSubscription() {
  return apiFetch<SubscriptionActionResponse | ApiEnvelope<SubscriptionActionResponse>>('/billing/resume', { method: 'POST' }).then(unwrapApiData);
}

export function getBillingHistory() {
  return apiFetch<BillingHistory | ApiEnvelope<BillingHistory>>('/billing/history').then(unwrapApiData);
}
