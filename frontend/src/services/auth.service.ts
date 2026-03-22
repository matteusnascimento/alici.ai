import { apiFetch, clearAuthToken, setAuthToken } from './api';
import type { AuthResponse, LoginInput, RegisterInput, User } from '../types/auth';

export async function register(payload: RegisterInput) {
  const response = await apiFetch<AuthResponse>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
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
  return apiFetch<User>('/user/me');
}

export function logout() {
  clearAuthToken();
}
