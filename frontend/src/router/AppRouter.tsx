import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';

import { LoginForm } from '../components/auth/LoginForm';
import { RegisterForm } from '../components/auth/RegisterForm';
import { GoogleOAuthCallback } from '../components/auth/GoogleOAuthCallback';
import { LandingPage } from '../components/landing/LandingPage';
import { ChatPanel } from '../components/platform/ChatPanel';
import { DashboardPanel } from '../components/platform/DashboardPanel';
import { PlatformShell } from '../components/platform/PlatformShell';
import { AccountShell } from '../components/account/AccountShell';
import { AccountAppsPage } from '../components/account/pages/AccountAppsPage';
import { AccountAppsActionsPage } from '../components/account/pages/AccountAppsActionsPage';
import { AccountAppsStatusPage } from '../components/account/pages/AccountAppsStatusPage';
import { AccountChatsPage } from '../components/account/pages/AccountChatsPage';
import { AccountDataPage } from '../components/account/pages/AccountDataPage';
import { AccountHelpPage } from '../components/account/pages/AccountHelpPage';
import { AccountHomePage } from '../components/account/pages/AccountHomePage';
import { AccountLegalPage } from '../components/account/pages/AccountLegalPage';
import { AccountNotificationsPage } from '../components/account/pages/AccountNotificationsPage';
import { AccountPersonalizationPage } from '../components/account/pages/AccountPersonalizationPage';
import { AccountPlatformStatusPage } from '../components/account/pages/AccountPlatformStatusPage';
import { AccountProfilePage } from '../components/account/pages/AccountProfilePage';
import { AccountSecurityPage } from '../components/account/pages/AccountSecurityPage';
import { BillingCancelPage } from '../components/account/pages/BillingCancelPage';
import { BillingSuccessPage } from '../components/account/pages/BillingSuccessPage';
import { AssetsStudioPage } from '../components/studio/v2/AssetsStudioPage';
import { AiCreativeStudioPage } from '../components/studio/v2/AiCreativeStudioPage';
import { BannerStudioPage } from '../components/studio/v2/BannerStudioPage';
import { CaptionsStudioPage } from '../components/studio/v2/CaptionsStudioPage';
import { BrandStudioPage } from '../components/studio/v2/BrandStudioPage';
import { ExportsStudioPage } from '../components/studio/v2/ExportsStudioPage';
import { PhotoEditorStudioPage } from '../components/studio/v2/PhotoEditorStudioPage';
import { PosterStudioPage } from '../components/studio/v2/PosterStudioPage';
import { ProjectsStudioPage } from '../components/studio/v2/ProjectsStudioPage';
import { RemoveBackgroundStudioPage } from '../components/studio/v2/RemoveBackgroundStudioPage';
import { StoryStudioPage } from '../components/studio/v2/StoryStudioPage';
import { StudioHomePage } from '../components/studio/v2/StudioHomePage';
import { TemplatesStudioPage } from '../components/studio/v2/TemplatesStudioPage';
import { UnifiedStudioEditorPage } from '../components/studio/v2/UnifiedStudioEditorPage';
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

import { MarketingShell } from '../components/marketing/MarketingShell';
import { MarketingProjectsPage } from '../components/marketing/MarketingProjectsPage';
import { MarketingProjectWorkspace } from '../components/marketing/MarketingProjectWorkspace';
import { IntegrationsPage } from '../components/integrations/IntegrationsPage';
import { RevenueIntelligencePage } from '../components/revenue/RevenueIntelligencePage';
import { BusinessModulePage } from '../components/modules/BusinessModulePage';

import { ProtectedRoute } from './ProtectedRoute';

function AuthLayout({ title, subtitle, children }: { title: string; subtitle: string; children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  if (isAuthenticated) {
    return <Navigate replace to="/app/dashboard" />;
  }
  return (
    <main className="grid min-h-screen bg-ink px-6 py-10 text-[var(--text-primary)] lg:grid-cols-[minmax(0,1fr)_520px] lg:gap-8">
      <section className="hidden min-h-[calc(100vh-5rem)] rounded-[2rem] border border-white/10 bg-gradient-to-br from-cyan/20 via-white/[0.04] to-black/20 p-10 shadow-soft lg:flex lg:flex-col lg:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.35em] text-cyan">AXI Platform</p>
          <h2 className="mt-6 max-w-xl font-display text-5xl font-bold leading-tight">Entre, conecte seus canais e deixe a IA trabalhar com seus dados reais.</h2>
          <p className="mt-5 max-w-lg text-base leading-7 text-slate-300">
            Login simples com email ou Google, CRM, atendimento, Studio e automações em um único cockpit.
          </p>
        </div>
        <div className="grid grid-cols-3 gap-3 text-sm">
          {['Chat omnichannel', 'AXI Studio', 'CRM com IA'].map((item) => (
            <div key={item} className="rounded-2xl border border-white/10 bg-black/20 p-4 font-semibold text-slate-200">{item}</div>
          ))}
        </div>
      </section>

      <section className="mx-auto flex w-full max-w-lg flex-col justify-center rounded-[2rem] border border-white/10 bg-white/5 p-8 shadow-soft backdrop-blur lg:mx-0">
        <p className="text-sm uppercase tracking-[0.3em] text-cyan">AXI Platform</p>
        <h1 className="mt-4 font-display text-4xl font-bold">{title}</h1>
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
        <Route element={<GoogleOAuthCallback />} path="/auth/google/callback" />
        <Route element={<ProtectedRoute />}>
          <Route element={<PlatformShell />} path="/app">
            <Route element={<Navigate replace to="/app/dashboard" />} index />
            <Route element={<DashboardPanel />} path="dashboard" />
            <Route element={<RevenueIntelligencePage />} path="revenue" />
            <Route element={<ChatPanel />} path="chat" />
            <Route path="crm">
              <Route index element={<Navigate replace to="/app/crm/negocios" />} />
              <Route path=":moduleId" element={<BusinessModulePage group="crm" />} />
            </Route>
            <Route path="cs">
              <Route index element={<Navigate replace to="/app/cs/jornada" />} />
              <Route path=":moduleId" element={<BusinessModulePage group="cs" />} />
            </Route>
            <Route path="analytics">
              <Route index element={<Navigate replace to="/app/analytics/analises" />} />
              <Route path=":moduleId" element={<BusinessModulePage group="analytics" />} />
            </Route>
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
              <Route path="editor" element={<UnifiedStudioEditorPage />} />
              <Route path="editor/video" element={<VideoEditorStudioPage />} />
              <Route path="editor/video/:projectId" element={<VideoEditorStudioPage />} />

              <Route path="tools/photo-editor" element={<PhotoEditorStudioPage />} />
              <Route path="tools/remove-background" element={<RemoveBackgroundStudioPage />} />
              <Route path="tools/ad" element={<PosterStudioPage />} />
              <Route path="tools/story" element={<StoryStudioPage />} />
              <Route path="tools/caption" element={<CaptionsStudioPage />} />
              <Route path="tools/cta" element={<CaptionsStudioPage mode="cta" />} />
              <Route path="tools/copy" element={<CaptionsStudioPage mode="promo" />} />

              <Route path="video-editor/*" element={<Navigate replace to="/app/studio/editor/video" />} />
              <Route path="photo-editor/*" element={<Navigate replace to="/app/studio/tools/photo-editor" />} />
              <Route path="poster/*" element={<Navigate replace to="/app/studio/tools/ad" />} />
              <Route path="banner" element={<Navigate replace to="/app/studio/tools/ad" />} />
              <Route path="story" element={<Navigate replace to="/app/studio/tools/story" />} />
              <Route path="story/new" element={<Navigate replace to="/app/studio/tools/story" />} />
              <Route path="ad-builder" element={<Navigate replace to="/app/studio/tools/ad" />} />
              <Route path="caption-generator/*" element={<Navigate replace to="/app/studio/tools/caption" />} />
              <Route path="copy-generator/*" element={<Navigate replace to="/app/studio/tools/copy" />} />

              <Route path="remove-background" element={<RemoveBackgroundStudioPage />} />
              <Route path="projects" element={<ProjectsStudioPage />} />
              <Route path="exports" element={<ExportsStudioPage />} />
              
              {/* LIBRARY - MANAGE */}
              <Route path="brand-kit/*" element={<BrandStudioPage />} />
              <Route path="templates/*" element={<TemplatesStudioPage />} />
              <Route path="assets/*" element={<AssetsStudioPage />} />
              <Route path="ai-creative/*" element={<AiCreativeStudioPage />} />
              
              {/* DEPRECATED - Redirects for backwards compatibility */}
              <Route path="brand" element={<BrandStudioPage />} />
            </Route>
            <Route path="marketing" element={<MarketingShell />}>
              <Route index element={<MarketingProjectsPage />} />
              <Route path="projects/:projectId" element={<MarketingProjectWorkspace />} />
            </Route>
            <Route path="integrations" element={<IntegrationsPage />} />
            <Route path="billing/success" element={<BillingSuccessPage />} />
            <Route path="billing/cancel" element={<BillingCancelPage />} />
            <Route path="account" element={<AccountShell />}>
              <Route index element={<Navigate replace to="overview" />} />
              <Route path="overview" element={<AccountHomePage />} />
              <Route path="profile" element={<AccountProfilePage />} />
              <Route path="personalization" element={<AccountPersonalizationPage />} />
              <Route path="notifications" element={<AccountNotificationsPage />} />
              <Route path="applications" element={<AccountAppsPage />} />
              <Route path="applications/status" element={<AccountAppsStatusPage />} />
              <Route path="applications/actions" element={<AccountAppsActionsPage />} />
              <Route path="data-controls" element={<AccountDataPage />} />
              <Route path="security" element={<AccountSecurityPage />} />
              <Route path="archived-chats" element={<AccountChatsPage />} />
              <Route path="language-appearance" element={<Navigate replace to="/app/account/personalization" />} />
              <Route path="help" element={<AccountHelpPage />} />
              <Route path="help/status" element={<AccountPlatformStatusPage />} />
              <Route path="legal" element={<AccountLegalPage />} />

              <Route path="apps" element={<Navigate replace to="/app/account/applications" />} />
              <Route path="apps/status" element={<Navigate replace to="/app/account/applications/status" />} />
              <Route path="apps/actions" element={<Navigate replace to="/app/account/applications/actions" />} />
              <Route path="data" element={<Navigate replace to="/app/account/data-controls" />} />
              <Route path="chats" element={<Navigate replace to="/app/account/archived-chats" />} />
              <Route path="language" element={<Navigate replace to="/app/account/personalization" />} />
            </Route>
          </Route>
        </Route>
        <Route element={<Navigate replace to="/" />} path="*" />
      </Routes>
    </BrowserRouter>
  );
}
