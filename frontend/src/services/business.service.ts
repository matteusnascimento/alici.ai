import { apiFetch } from './api';

type ApiEnvelope<T> = {
  status?: string;
  data?: T;
};

function unwrapApiData<T>(value: T | ApiEnvelope<T>): T {
  if (value && typeof value === 'object' && 'data' in value) {
    return (value as ApiEnvelope<T>).data as T;
  }
  return value as T;
}

export interface BusinessSummary {
  contacts: number;
  deals: number;
  open_deals: number;
  pipeline_value_cents: number;
  won_value_cents: number;
  products: number;
  calls_today: number;
}

export interface BusinessPipeline {
  id: number;
  name: string;
  description?: string | null;
  stages?: string[];
  is_default?: boolean;
  created_at?: string;
}

export interface BusinessContact {
  id: number;
  name: string;
  email?: string | null;
  phone?: string | null;
  company?: string | null;
  status: string;
  source?: string | null;
  last_interaction_at?: string;
}

export interface BusinessDeal {
  id: number;
  title: string;
  value_cents: number;
  currency?: string;
  stage: string;
  status: string;
  probability: number;
  contact_id?: number | null;
  pipeline_id?: number | null;
  expected_close_date?: string | null;
  created_at?: string;
}

export interface BusinessProduct {
  id: number;
  name: string;
  description?: string | null;
  price_cents: number;
  currency?: string;
  status: string;
  created_at?: string;
}

export interface BusinessCall {
  id: number;
  contact_id?: number | null;
  phone: string;
  direction: string;
  outcome: string;
  duration_seconds: number;
  notes?: string | null;
  created_at?: string;
}

export interface BusinessGenericRecord {
  id: number;
  title?: string;
  name?: string;
  body?: string;
  description?: string | null;
  status?: string;
  value_cents?: number;
  scheduled_at?: string | null;
  due_at?: string | null;
  signed_at?: string | null;
  priority?: string;
  category?: string;
  tracking_code?: string | null;
  notes?: string | null;
  created_at?: string;
}

export interface BusinessRevenueGoal {
  id: number;
  year: number;
  month: number;
  target_cents: number;
}

export type BusinessResource =
  | 'contacts'
  | 'deals'
  | 'products'
  | 'pipelines'
  | 'calls'
  | 'groups'
  | 'meetings'
  | 'contracts'
  | 'tasks'
  | 'quick-messages'
  | 'logistics'
  | 'revenue-goals';

export function getBusinessSummary() {
  return apiFetch<BusinessSummary | ApiEnvelope<BusinessSummary>>('/business/summary').then(unwrapApiData);
}

export function listBusinessResource<T>(resource: BusinessResource, query = '') {
  const suffix = query ? `?search=${encodeURIComponent(query)}` : '';
  return apiFetch<T[] | ApiEnvelope<T[]>>(`/business/${resource}${suffix}`).then(unwrapApiData);
}

export function createBusinessResource<T>(resource: BusinessResource, payload: Record<string, unknown>) {
  return apiFetch<T | ApiEnvelope<T>>(`/business/${resource}`, {
    method: 'POST',
    body: JSON.stringify(payload),
  }).then(unwrapApiData);
}

export function updateBusinessStatus<T>(resource: 'contacts' | 'deals' | 'products', id: number, status: string) {
  return apiFetch<T | ApiEnvelope<T>>(`/business/${resource}/${id}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ status }),
  }).then(unwrapApiData);
}
