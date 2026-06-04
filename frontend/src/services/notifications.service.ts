import { apiFetch } from './api';
import type { SystemNotification } from '../types/notifications';

export function listNotifications() {
  return apiFetch<SystemNotification[]>('/notifications');
}

export function markNotificationRead(id: number) {
  return apiFetch<SystemNotification>(`/notifications/${id}/read`, { method: 'PATCH' });
}

export function markAllNotificationsRead() {
  return apiFetch<SystemNotification[]>('/notifications/read-all', { method: 'PATCH' });
}
