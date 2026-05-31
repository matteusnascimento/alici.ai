import { apiFetch } from './api';

export interface AdminMetric {
  label: string;
  value: number;
}

export interface AdminUser {
  id: number;
  name: string;
  email: string;
  role: string;
  plan: string;
}

export interface AdminOverview {
  empresas: string[];
  usuarios: AdminUser[];
  permissoes: string[];
  billing: AdminMetric[];
  seguranca: AdminMetric[];
  auditoria: AdminMetric[];
}

export function getAdminOverview() {
  return apiFetch<AdminOverview>('/admin/overview');
}
