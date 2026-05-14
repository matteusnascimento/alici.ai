import { apiFetch } from './api';
import type { DashboardStats } from '../types/dashboard';

export interface DashboardOverview {
  total_messages: number;
  total_agents: number;
  active_agents: number;
  current_plan: string;
}

export interface DashboardUsage {
  messages_used: number;
  messages_limit: number;
  agents_used: number;
  agents_limit: number;
}

export interface DashboardMetricItem {
  key: string;
  value: number;
}

export interface DashboardMetrics {
  items: DashboardMetricItem[];
}

export interface DashboardAIHealth {
  provider: string;
  status: 'ok' | 'error';
  model: string;
  latency_ms: number;
  error_type?: string | null;
  status_code?: number | null;
}

export interface DashboardAIMetrics {
  window: '24h' | '7d' | '30d';
  total_requests: number;
  success_requests: number;
  error_requests: number;
  rate_limit_429: number;
  avg_latency_ms: number;
  trend: Array<{ label: string; value: number }>;
  trend_429: Array<{ label: string; value: number }>;
}

export function getDashboardStats() {
  return apiFetch<DashboardStats>('/dashboard/stats');
}

export function getDashboardOverview(): Promise<DashboardOverview> {
  return apiFetch<DashboardOverview>('/dashboard/overview');
}

export function getDashboardUsage(): Promise<DashboardUsage> {
  return apiFetch<DashboardUsage>('/dashboard/usage');
}

export function getDashboardMetrics(): Promise<DashboardMetrics> {
  return apiFetch<DashboardMetrics>('/dashboard/metrics');
}

export function getDashboardAIHealth(): Promise<DashboardAIHealth> {
  return apiFetch<DashboardAIHealth>('/dashboard/ai-health');
}

export function getDashboardAIMetrics(window: '24h' | '7d' | '30d' = '24h'): Promise<DashboardAIMetrics> {
  return apiFetch<DashboardAIMetrics>(`/dashboard/ai-metrics?window=${window}`);
}
