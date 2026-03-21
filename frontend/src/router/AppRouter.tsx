import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';

import { LoginForm } from '../components/auth/LoginForm';
import { RegisterForm } from '../components/auth/RegisterForm';
import { LandingPage } from '../components/landing/LandingPage';
import { AccountPanel } from '../components/platform/AccountPanel';
import { AgentsPanel } from '../components/platform/AgentsPanel';
import { ChatPanel } from '../components/platform/ChatPanel';
import { DashboardPanel } from '../components/platform/DashboardPanel';
import { MarketingPanel } from '../components/platform/MarketingPanel';
import { PlatformShell } from '../components/platform/PlatformShell';
import { useAuth } from '../hooks/useAuth';

import { ProtectedRoute } from './ProtectedRoute';

function AuthLayout({ title, subtitle, children }: { title: string; subtitle: string; children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  if (isAuthenticated) {
    return <Navigate replace to="/app/dashboard" />;
  }
  return (
    <main className="flex min-h-screen items-center justify-center bg-ink px-6 py-12 text-white">
      <section className="w-full max-w-lg rounded-[2rem] border border-white/10 bg-white/5 p-8 shadow-soft backdrop-blur">
        <p className="text-sm uppercase tracking-[0.3em] text-cyan">AXI Platform</p>
        <h1 className="mt-4 font-display text-4xl">{title}</h1>
        <p className="mt-3 text-slate-300">{subtitle}</p>
        <div className="mt-8">{children}</div>
      </section>
    </main>
  );
}

export function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<LandingPage />} path="/" />
        <Route
          element={(
            <AuthLayout subtitle="Acesse sua área privada para operar chat, agentes e marketing." title="Login">
              <LoginForm />
            </AuthLayout>
          )}
          path="/login"
        />
        <Route
          element={(
            <AuthLayout subtitle="Crie sua conta para ativar o cockpit AXI." title="Cadastro">
              <RegisterForm />
            </AuthLayout>
          )}
          path="/register"
        />
        <Route element={<ProtectedRoute />}>
          <Route element={<PlatformShell />} path="/app">
            <Route element={<Navigate replace to="/app/dashboard" />} index />
            <Route element={<DashboardPanel />} path="dashboard" />
            <Route element={<ChatPanel />} path="chat" />
            <Route element={<AgentsPanel />} path="agents" />
            <Route element={<MarketingPanel />} path="marketing" />
            <Route element={<AccountPanel />} path="account" />
          </Route>
        </Route>
        <Route element={<Navigate replace to="/" />} path="*" />
      </Routes>
    </BrowserRouter>
  );
}
