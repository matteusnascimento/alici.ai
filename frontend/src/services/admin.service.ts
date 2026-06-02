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

export interface AdminCompany {
  name: string;
  email: string | null;
  plan: string;
  status: string;
  users_count: number;
  created_at: string | null;
}

export interface AdminOverview {
  empresas: AdminCompany[];
  usuarios: AdminUser[];
  permissoes: string[];
  billing: AdminMetric[];
  seguranca: AdminMetric[];
  auditoria: AdminMetric[];
}

export function getAdminOverview() {
  return apiFetch<AdminOverview>('/admin/overview');
}
