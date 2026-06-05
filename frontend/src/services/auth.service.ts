import { apiFetch, clearAuthToken, setAuthToken } from './api';
import type { AuthResponse, LoginInput, RegisterInput, User } from '../types/auth';

function normalizeUsername(payload: RegisterInput) {
  return (payload.username || payload.email.split('@')[0]).trim().replace(/\s+/g, '').toLowerCase();
}

export async function register(payload: RegisterInput) {
  const response = await apiFetch<AuthResponse>('/auth/register', {
    method: 'POST',
    body: JSON.stringify({
      name: payload.name || payload.username || payload.email,
      username: normalizeUsername(payload),
      email: payload.email,
      phone: payload.phone || null,
      password: payload.password,
    }),
  });
  setAuthToken(response.access_token);
  return response;
}

export async function login(payload: LoginInput) {
  const response = await apiFetch<AuthResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  setAuthToken(response.access_token);
  return response;
}

export async function getMe() {
  return apiFetch<User>('/auth/me');
}

export function logout() {
  clearAuthToken();
}
