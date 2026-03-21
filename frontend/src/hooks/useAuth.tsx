import { createContext, useContext, useEffect, useMemo, useState } from 'react';

import { getMe, login as loginRequest, logout as logoutRequest, register as registerRequest } from '../services/auth.service';
import { clearAuthToken, getAuthToken, setUnauthorizedHandler } from '../services/api';
import type { LoginInput, RegisterInput, User } from '../types/auth';

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  ready: boolean;
  isAuthenticated: boolean;
  login: (payload: LoginInput) => Promise<void>;
  register: (payload: RegisterInput) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    async function bootstrap() {
      const token = getAuthToken();
      if (!token) {
        setReady(true);
        return;
      }
      try {
        const me = await getMe();
        setUser(me);
      } catch {
        clearAuthToken();
        setUser(null);
      } finally {
        setReady(true);
      }
    }
    void bootstrap();
  }, []);

  useEffect(() => {
    setUnauthorizedHandler(() => {
      clearAuthToken();
      setUser(null);
    });
    return () => setUnauthorizedHandler(null);
  }, []);

  async function login(payload: LoginInput) {
    setLoading(true);
    try {
      const response = await loginRequest(payload);
      setUser(response.user);
    } finally {
      setLoading(false);
    }
  }

  async function register(payload: RegisterInput) {
    setLoading(true);
    try {
      const response = await registerRequest(payload);
      setUser(response.user);
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    logoutRequest();
    setUser(null);
  }

  const value = useMemo(
    () => ({ user, loading, ready, isAuthenticated: Boolean(user), login, register, logout }),
    [loading, ready, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider');
  }
  return context;
}
