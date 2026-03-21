import { apiFetch } from './api';
import type { DashboardStats } from '../types/dashboard';

export function getDashboardStats() {
  return apiFetch<DashboardStats>('/dashboard/stats');
}
