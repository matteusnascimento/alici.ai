export interface PlanLimit {
  key: string;
  value: number;
}

export interface BillingPlan {
  id: string;
  name: string;
  monthly_price: number;
  yearly_price: number | null;
  features: string[];
  limits: PlanLimit[];
  active: boolean;
}

export interface CurrentSubscription {
  plan_id: string;
  plan_name: string;
  status: string;
  billing_cycle: string;
  monthly_price: number;
  yearly_price: number | null;
  auto_renew: boolean;
  started_at: string | null;
}

export interface UpgradePayload {
  plan_id: string;
  billing_cycle: 'monthly' | 'yearly';
}

export interface UpgradeResponse {
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
