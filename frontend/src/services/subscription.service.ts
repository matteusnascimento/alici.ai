import { apiFetch } from './api';
import type { BillingPlan, CurrentSubscription } from '../types/billing';

export function getSubscription() {
  return apiFetch<CurrentSubscription>('/account/subscription');
}

export function getSubscriptionPlans() {
  return apiFetch<BillingPlan[]>('/billing/plans');
}
