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
