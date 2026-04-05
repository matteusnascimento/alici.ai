import { BrowserRouter, Navigate, Route, Routes, useLocation } from 'react-router-dom';

import { LoginForm } from '../components/auth/LoginForm';
import { RegisterForm } from '../components/auth/RegisterForm';
import { LandingPage } from '../components/landing/LandingPage';
import { ChatPanel } from '../components/platform/ChatPanel';
import { DashboardPanel } from '../components/platform/DashboardPanel';
import { PlatformShell } from '../components/platform/PlatformShell';
import { AccountShell } from '../components/account/AccountShell';
import { AccountAppsPage } from '../components/account/pages/AccountAppsPage';
import { AccountChatsPage } from '../components/account/pages/AccountChatsPage';
import { AccountDataPage } from '../components/account/pages/AccountDataPage';
import { AccountHelpPage } from '../components/account/pages/AccountHelpPage';
import { AccountHomePage } from '../components/account/pages/AccountHomePage';
import { AccountLanguagePage } from '../components/account/pages/AccountLanguagePage';
import { AccountLegalPage } from '../components/account/pages/AccountLegalPage';
import { AccountNotificationsPage } from '../components/account/pages/AccountNotificationsPage';
import { AccountPersonalizationPage } from '../components/account/pages/AccountPersonalizationPage';
import { AccountProfilePage } from '../components/account/pages/AccountProfilePage';
import { AccountSecurityPage } from '../components/account/pages/AccountSecurityPage';
import { AssetsStudioPage } from '../components/studio/v2/AssetsStudioPage';
import { BannerStudioPage } from '../components/studio/v2/BannerStudioPage';
import { CaptionsStudioPage } from '../components/studio/v2/CaptionsStudioPage';
import { PhotoEditorStudioPage } from '../components/studio/v2/PhotoEditorStudioPage';
import { PosterStudioPage } from '../components/studio/v2/PosterStudioPage';
import { ProjectsStudioPage } from '../components/studio/v2/ProjectsStudioPage';
import { RemoveBackgroundStudioPage } from '../components/studio/v2/RemoveBackgroundStudioPage';
import { RetouchStudioPage } from '../components/studio/v2/RetouchStudioPage';
import { StoryStudioPage } from '../components/studio/v2/StoryStudioPage';
import { StudioHomePage } from '../components/studio/v2/StudioHomePage';
import { TemplatesStudioPage } from '../components/studio/v2/TemplatesStudioPage';
import { VideoEditorStudioPage } from '../components/studio/v2/VideoEditorStudioPage';
import { useAuth } from '../hooks/useAuth';
import { AgentActionsPage } from '../components/agents/v2/AgentActionsPage';
import { AgentAnalyticsPage } from '../components/agents/v2/AgentAnalyticsPage';
import { AgentChannelsPage } from '../components/agents/v2/AgentChannelsPage';
import { AgentCreatePage } from '../components/agents/v2/AgentCreatePage';
import { AgentKnowledgePage } from '../components/agents/v2/AgentKnowledgePage';
import { AgentLogsPage } from '../components/agents/v2/AgentLogsPage';
import { AgentOverviewPage } from '../components/agents/v2/AgentOverviewPage';
import { AgentSettingsPage } from '../components/agents/v2/AgentSettingsPage';
import { AgentTemplatesPage } from '../components/agents/v2/AgentTemplatesPage';
import { AgentTestPage } from '../components/agents/v2/AgentTestPage';
import { AgentsMainPage } from '../components/agents/v2/AgentsMainPage';
import { AgentsShell } from '../components/agents/v2/AgentsShell';
import { AgentWorkspaceShell } from '../components/agents/v2/AgentWorkspaceShell';

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

function LegacyStudioRedirect() {
  const location = useLocation();
  const suffix = location.pathname.replace('/app/marketing', '');
  return <Navigate replace to={`/app/studio${suffix}${location.search}`} />;
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
            <Route path="agents" element={<AgentsShell />}>
              <Route index element={<AgentsMainPage />} />
              <Route path="create" element={<AgentCreatePage />} />
              <Route path="templates" element={<AgentTemplatesPage />} />
              <Route path=":id" element={<AgentWorkspaceShell />}>
                <Route index element={<Navigate replace to="overview" />} />
                <Route path="overview" element={<AgentOverviewPage />} />
                <Route path="channels" element={<AgentChannelsPage />} />
                <Route path="knowledge" element={<AgentKnowledgePage />} />
                <Route path="actions" element={<AgentActionsPage />} />
                <Route path="test" element={<AgentTestPage />} />
                <Route path="logs" element={<AgentLogsPage />} />
                <Route path="analytics" element={<AgentAnalyticsPage />} />
                <Route path="settings" element={<AgentSettingsPage />} />
              </Route>
            </Route>
            <Route path="studio">
              <Route index element={<StudioHomePage />} />
              <Route path="poster" element={<PosterStudioPage />} />
              <Route path="story" element={<StoryStudioPage />} />
              <Route path="banner" element={<BannerStudioPage />} />
              <Route path="photo-editor" element={<PhotoEditorStudioPage />} />
              <Route path="video-editor" element={<VideoEditorStudioPage />} />
              <Route path="remove-background" element={<RemoveBackgroundStudioPage />} />
              <Route path="retouch" element={<RetouchStudioPage />} />
              <Route path="legendas" element={<CaptionsStudioPage />} />
              <Route path="projects" element={<ProjectsStudioPage />} />
              <Route path="templates" element={<TemplatesStudioPage />} />
              <Route path="assets" element={<AssetsStudioPage />} />
              <Route path="ads" element={<BannerStudioPage />} />
              <Route path="captions" element={<CaptionsStudioPage />} />
              <Route path="library" element={<TemplatesStudioPage />} />
              <Route path="cloud" element={<AssetsStudioPage />} />
            </Route>
            <Route path="marketing/*" element={<LegacyStudioRedirect />} />
            <Route path="account" element={<AccountShell />}>
              <Route index element={<AccountHomePage />} />
              <Route path="profile" element={<AccountProfilePage />} />
              <Route path="personalization" element={<AccountPersonalizationPage />} />
              <Route path="notifications" element={<AccountNotificationsPage />} />
              <Route path="apps" element={<AccountAppsPage />} />
              <Route path="data" element={<AccountDataPage />} />
              <Route path="security" element={<AccountSecurityPage />} />
              <Route path="chats" element={<AccountChatsPage />} />
              <Route path="language" element={<AccountLanguagePage />} />
              <Route path="help" element={<AccountHelpPage />} />
              <Route path="legal" element={<AccountLegalPage />} />
            </Route>
          </Route>
        </Route>
        <Route element={<Navigate replace to="/" />} path="*" />
      </Routes>
    </BrowserRouter>
  );
}
