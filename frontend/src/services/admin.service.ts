import { apiFetch } from './api';
import type { BillingHistoryItem, BillingUsageItem, CurrentSubscription, PlanLimit } from '../types/billing';

export type AdminPermissionLevel = 'none' | 'read' | 'write' | 'admin';
export type AdminPermissionMap = Record<string, AdminPermissionLevel>;

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
  job_title: string | null;
  phone: string | null;
  company: string | null;
  status: 'active' | 'inactive' | 'pending';
  last_login_at: string | null;
  created_at: string | null;
  disabled_at: string | null;
  email_verified: boolean;
  permissions: AdminPermissionMap;
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

export interface AdminCompanyCreatePayload {
  nome: string;
  razao_social?: string;
  cnpj?: string;
  email: string;
  telefone?: string;
  plano: 'basic' | 'pro' | 'enterprise';
  modules: string[];
}

export interface AdminUserInvitePayload {
  name: string;
  email: string;
  job_title?: string;
  phone?: string;
  permissions: AdminPermissionMap;
}

export interface AdminUserInviteResponse {
  user: AdminUser;
  email_delivery: 'sent' | 'unavailable';
  message: string;
  invite_token: string | null;
}

export interface AdminUserUpdatePayload {
  name?: string;
  email?: string;
  job_title?: string;
  phone?: string;
  plan?: string;
}

export interface AdminUserActionResponse {
  message: string;
  user: AdminUser | null;
  reset_token?: string | null;
}

export interface AdminPermissionsResponse {
  user_id: number;
  permissions: AdminPermissionMap;
}

export interface AdminSecurityEvent {
  id: number;
  user_id: number | null;
  user_name: string | null;
  user_email: string | null;
  event_type: string;
  status: string;
  created_at: string | null;
  expires_at: string | null;
  revoked_at: string | null;
}

export interface AdminSecurityResponse {
  last_logins: AdminSecurityEvent[];
  active_sessions: AdminSecurityEvent[];
  open_sessions: AdminSecurityEvent[];
  login_attempts: AdminSecurityEvent[];
  revoked_tokens: AdminSecurityEvent[];
}

export interface AdminAuditEvent {
  id: number;
  data: string | null;
  usuario: string | null;
  acao: string;
  origem: string;
  detalhes: Record<string, unknown> | null;
}

export interface AdminAuditResponse {
  events: AdminAuditEvent[];
}

export interface AdminBillingResponse {
  current: CurrentSubscription;
  usage: BillingUsageItem[];
  limits: PlanLimit[];
  events: BillingHistoryItem[];
  stripe_configured: boolean;
  message: string | null;
}

export const ADMIN_PERMISSION_MODULES = [
  { key: 'revenue', label: 'Revenue' },
  { key: 'chats', label: 'Chats' },
  { key: 'assistant', label: 'AXI Assistant' },
  { key: 'marketing', label: 'Marketing' },
  { key: 'studio', label: 'Studio' },
  { key: 'integrations', label: 'Integrations' },
  { key: 'admin', label: 'Administracao' },
] as const;

export function createEmptyPermissions(): AdminPermissionMap {
  return ADMIN_PERMISSION_MODULES.reduce<AdminPermissionMap>((acc, module) => {
    acc[module.key] = 'none';
    return acc;
  }, {});
}

export function getAdminOverview() {
  return apiFetch<AdminOverview>('/admin/overview');
}

export function createAdminCompany(payload: AdminCompanyCreatePayload) {
  return apiFetch<AdminCompany>('/admin/companies', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function listAdminUsers() {
  return apiFetch<AdminUser[]>('/admin/users');
}

export function inviteAdminUser(payload: AdminUserInvitePayload) {
  return apiFetch<AdminUserInviteResponse>('/admin/users/invite', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function updateAdminUser(userId: number, payload: AdminUserUpdatePayload) {
  return apiFetch<AdminUser>(`/admin/users/${userId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export function disableAdminUser(userId: number) {
  return apiFetch<AdminUserActionResponse>(`/admin/users/${userId}/disable`, { method: 'POST' });
}

export function enableAdminUser(userId: number) {
  return apiFetch<AdminUserActionResponse>(`/admin/users/${userId}/enable`, { method: 'POST' });
}

export function resetAdminUserPassword(userId: number) {
  return apiFetch<AdminUserActionResponse>(`/admin/users/${userId}/reset-password`, { method: 'POST' });
}

export function getAdminUserPermissions(userId: number) {
  return apiFetch<AdminPermissionsResponse>(`/admin/users/${userId}/permissions`);
}

export function saveAdminUserPermissions(userId: number, permissions: AdminPermissionMap) {
  return apiFetch<AdminPermissionsResponse>(`/admin/users/${userId}/permissions`, {
    method: 'PUT',
    body: JSON.stringify({ permissions }),
  });
}

export function getAdminSecurity() {
  return apiFetch<AdminSecurityResponse>('/admin/security');
}

export function getAdminAudit() {
  return apiFetch<AdminAuditResponse>('/admin/audit');
}

export function getAdminBilling() {
  return apiFetch<AdminBillingResponse>('/admin/billing');
}
