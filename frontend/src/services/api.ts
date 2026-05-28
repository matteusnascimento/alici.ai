export const API_BASE_URL =
  import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://127.0.0.1:8000' : '');
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

function extractErrorMessage(data: unknown, fallback: string): string {
  if (typeof data === 'object' && data !== null) {
    const payload = data as { message?: unknown; detail?: unknown };
    if (typeof payload.message === 'string') {
      return payload.message;
    }
    if (typeof payload.detail === 'string') {
      return payload.detail;
    }
    if (typeof payload.detail === 'object' && payload.detail !== null) {
      const detail = payload.detail as { message?: unknown };
      if (typeof detail.message === 'string') {
        return detail.message;
      }
    }
  }
  return fallback;
}

async function parseResponse(response: Response): Promise<unknown> {
  const text = await response.text();
  if (!text) {
    return null;
  }
  try {
    return JSON.parse(text);
  } catch {
    return { detail: text };
  }
}

export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getAuthToken();
  const headers = new Headers(init.headers || {});
  const isFormDataBody = typeof FormData !== 'undefined' && init.body instanceof FormData;

  if (init.body !== undefined && !isFormDataBody && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  } catch {
    throw new ApiError('Servidor indisponivel. Verifique sua conexao.', 0);
  }

  const data = await parseResponse(response);

  if (response.status === 401) {
    const isAuthRequest = path === '/auth/login' || path === '/auth/register';
    if (!isAuthRequest && unauthorizedHandler) {
      unauthorizedHandler();
    }
    const message = isAuthRequest
      ? extractErrorMessage(data, 'Email ou senha invalidos.')
      : extractErrorMessage(data, 'Sessao expirada. Faca login novamente.');
    throw new ApiError(message, 401, data);
  }

  if (response.status === 403) {
    throw new ApiError(
      extractErrorMessage(data, 'Acesso negado. Voce nao tem permissao para esta acao.'),
      403,
      data,
    );
  }

  if (response.status >= 500) {
    throw new ApiError(
      extractErrorMessage(data, 'Erro interno do servidor. Tente novamente mais tarde.'),
      response.status,
      data,
    );
  }

  if (!response.ok) {
    throw new ApiError(extractErrorMessage(data, 'Operacao nao concluida.'), response.status, data);
  }

  return data as T;
}
