export interface PlanLimit {
  key: string;
  value: number;
}

export interface BillingPlanStripePrices {
  monthly: boolean;
  yearly: boolean;
}

export interface BillingPlan {
  id: string;
  name: string;
  monthly_price: number;
  yearly_price: number | null;
  features: string[];
  limits: PlanLimit[];
  active: boolean;
  checkout_available?: boolean;
  stripe_prices?: BillingPlanStripePrices;
}

export interface CurrentSubscription {
  plan_id: string;
  plan_name: string;
  status: string;
  billing_cycle: string;
  monthly_price: number;
  yearly_price: number | null;
  auto_renew: boolean;
  cancel_at_period_end: boolean;
  started_at: string | null;
  next_renewal_at: string | null;
  provider: string | null;
  stripe_customer_id: string | null;
}

export interface UpgradePayload {
  plan_id: string;
  billing_cycle: 'monthly' | 'yearly';
}

export interface UpgradeResponse {
  message: string;
  subscription: CurrentSubscription;
}

export interface CheckoutPayload {
  plan_id: string;
  billing_cycle: 'monthly' | 'yearly';
}

export interface CheckoutResponse {
  checkout_url: string;
  session_id: string;
}

export interface PortalResponse {
  portal_url: string;
}

export interface SubscriptionActionResponse {
  message: string;
  subscription: CurrentSubscription;
}

export interface BillingUsageItem {
  metric: string;
  used: number;
  limit: number;
}

export interface BillingUsage {
  items: BillingUsageItem[];
}

export interface BillingHistoryItem {
  id: number;
  event_type: string;
  amount: number;
  currency: string;
  description: string | null;
  stripe_event_id: string | null;
  status: string | null;
  created_at: string;
}

export interface BillingHistory {
  events: BillingHistoryItem[];
}
