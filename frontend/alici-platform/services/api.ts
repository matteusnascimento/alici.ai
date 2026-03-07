import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { clearSessionTokens, getAccessToken, getRefreshToken, setSessionTokens } from "@/services/authSession";

type RetryableRequest = InternalAxiosRequestConfig & { _retry?: boolean };

interface RefreshResponse {
  accessToken: string;
  refreshToken?: string;
}

const baseURL = process.env.NEXT_PUBLIC_API_URL;

export const api = axios.create({
  baseURL,
  timeout: 15000
});

let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = getRefreshToken();
  if (!refreshToken || !baseURL) return null;

  try {
    const { data } = await axios.post<RefreshResponse>(`${baseURL}/auth/refresh`, {
      refreshToken
    });

    setSessionTokens(data.accessToken, data.refreshToken);
    return data.accessToken;
  } catch {
    clearSessionTokens();
    return null;
  }
}

api.interceptors.request.use((config) => {
  const token = getAccessToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as RetryableRequest | undefined;
    const status = error.response?.status;

    if (!originalRequest || status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    if (!refreshPromise) {
      refreshPromise = refreshAccessToken().finally(() => {
        refreshPromise = null;
      });
    }

    const newToken = await refreshPromise;
    if (!newToken) {
      return Promise.reject(error);
    }

    originalRequest.headers.Authorization = `Bearer ${newToken}`;
    return api.request(originalRequest);
  }
);
