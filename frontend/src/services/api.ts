const API_URL = import.meta.env.VITE_API_URL || '/api';
const TOKEN_KEY = 'axi_token';

let unauthorizedHandler: (() => void) | null = null;

export class ApiError extends Error {
  status: number;
  details?: unknown;

  constructor(message: string, status: number, details?: unknown) {
    super(message);
    this.status = status;
    this.details = details;
  }
}

export function setUnauthorizedHandler(handler: (() => void) | null) {
  unauthorizedHandler = handler;
}

export function getAuthToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setAuthToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearAuthToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers = new Headers(init.headers || {});

  // Set Content-Type only for requests that carry a body (avoid breaking multipart uploads)
  if (init.body !== undefined && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  let response: Response;
  try {
    response = await fetch(`${API_URL}${path}`, { ...init, headers });
  } catch {
    throw new ApiError('Servidor indisponível. Verifique sua conexão.', 0);
  }

  if (response.status === 401) {
    if (unauthorizedHandler) {
      unauthorizedHandler();
    }
    throw new ApiError('Sessão expirada. Faça login novamente.', 401);
  }

  if (response.status === 403) {
    throw new ApiError('Acesso negado. Você não tem permissão para esta ação.', 403);
  }

  if (response.status >= 500) {
    throw new ApiError('Erro interno do servidor. Tente novamente mais tarde.', response.status);
  }

  const text = await response.text();
  let data: unknown = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { detail: text };
    }
  }
  if (!response.ok) {
    const detailValue =
      typeof data === 'object' && data !== null && 'detail' in data
        ? (data as { detail: unknown }).detail
        : 'Erro de rede';

    const detailMessage = typeof detailValue === 'string' ? detailValue : 'Operacao nao concluida.';
    throw new ApiError(detailMessage, response.status, detailValue);
  }
  return data as T;
}
