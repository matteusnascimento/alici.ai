import { Navigate, Outlet, useLocation } from 'react-router-dom';

import { useAuth } from '../hooks/useAuth';

export function ProtectedRoute() {
  const location = useLocation();
  const { isAuthenticated, ready } = useAuth();

  if (!ready) {
    return <div className="flex min-h-screen items-center justify-center bg-ink text-white">Carregando sessão...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate replace state={{ from: location }} to="/login" />;
  }

  return <Outlet />;
}
