import { Navigate, Outlet, useLocation } from 'react-router-dom';

import { useAuth } from '../hooks/useAuth';
import { useInitializeTheme } from '../hooks/useInitializeTheme';

export function ProtectedRoute() {
  const location = useLocation();
  const { isAuthenticated, ready } = useAuth();

  useInitializeTheme(ready && isAuthenticated);

  if (!ready) {
    return <div className="flex min-h-screen items-center justify-center bg-ink text-[var(--text-primary)]">Carregando sessão...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate replace state={{ from: location }} to="/login" />;
  }

  return <Outlet />;
}
