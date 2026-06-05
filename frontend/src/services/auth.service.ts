import { API_BASE_URL, apiFetch, clearAuthToken, setAuthToken } from './api';
import type { AuthResponse, LoginInput, RegisterInput, User } from '../types/auth';

type ApiAuthUser = {
  id: number;
  nome?: string;
  name?: string;
  username?: string;
  email: string;
  phone?: string | null;
  plano?: string;
  plan?: string;
  created_at?: string;
};

type ApiAuthResponse = Omit<AuthResponse, 'user'> & {
  usuario?: ApiAuthUser;
  user?: ApiAuthUser;
};

function normalizeUser(user: ApiAuthUser): User {
  return {
    id: user.id,
    name: user.name || user.nome || user.email,
    nome: user.nome || user.name || user.email,
    username: user.username || user.email,
    email: user.email,
    phone: user.phone ?? null,
    plan: user.plan || user.plano || 'free',
    plano: user.plano || user.plan || 'free',
    created_at: user.created_at,
  };
}

function normalizeUsername(payload: RegisterInput) {
  return (payload.username || payload.email.split('@')[0]).trim().replace(/\s+/g, '').toLowerCase();
}

function normalizeAuthResponse(response: ApiAuthResponse): AuthResponse {
  const apiUser = response.user || response.usuario;
  if (!apiUser) {
    throw new Error('Resposta de autenticacao invalida.');
  }
  return {
    access_token: response.access_token,
    refresh_token: response.refresh_token,
    token_type: response.token_type,
    user: normalizeUser(apiUser),
  };
}

export async function register(payload: RegisterInput) {
  await apiFetch('/auth/register', {
    method: 'POST',
    body: JSON.stringify({
      name: payload.name || payload.username || payload.email,
      username: normalizeUsername(payload),
      email: payload.email,
      phone: payload.phone || null,
      password: payload.password,
    }),
  });
  return login({ email: payload.email, password: payload.password });
}

export async function login(payload: LoginInput) {
  clearAuthToken();
  const response = await apiFetch<ApiAuthResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({
      email: payload.email,
      password: payload.password,
    }),
  });
  const normalized = normalizeAuthResponse(response);
  setAuthToken(normalized.access_token);
  return normalized;
}

export function startGoogleLogin() {
  window.location.assign(`${API_BASE_URL}/auth/google/start`);
}

export async function completeOAuthLogin(payload: Pick<AuthResponse, 'access_token' | 'refresh_token' | 'token_type'>) {
  if (!payload.access_token) {
    throw new Error('Token de acesso ausente.');
  }
  setAuthToken(payload.access_token);
  const user = await getMe();
  return {
    ...payload,
    user,
  };
}

export async function getMe() {
  const response = await apiFetch<{ usuario?: ApiAuthUser; user?: ApiAuthUser }>('/auth/me');
  const user = response.user || response.usuario;
  if (!user) {
    throw new Error('Sessao invalida.');
  }
  return normalizeUser(user);
}

export function logout() {
  clearAuthToken();
}
