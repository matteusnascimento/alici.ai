import { Outlet, useLocation } from 'react-router-dom';
import { useState } from 'react';

import { AppSidebar } from '../layout/AppSidebar';
import { Topbar } from './Topbar';
import { ErrorBoundary } from '../common/ErrorBoundary';

export function PlatformShell() {
  const location = useLocation();
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [desktopSidebarExpanded, setDesktopSidebarExpanded] = useState(false);
  const inStudioSection = location.pathname.startsWith('/app/studio');
  const hidePlatformTopbar = inStudioSection || location.pathname.startsWith('/app/marketing') || location.pathname.startsWith('/app/revenue');
  const fullBleedModule = location.pathname.startsWith('/app/studio/editor');

  return (
    <main className="min-h-screen bg-ink text-[var(--text-primary)]">
      <div className="flex min-h-screen">
        {fullBleedModule ? null : (
          <AppSidebar
            mobileOpen={mobileSidebarOpen}
            onMobileOpen={() => setMobileSidebarOpen(true)}
            onMobileClose={() => setMobileSidebarOpen(false)}
            onDesktopExpandedChange={setDesktopSidebarExpanded}
          />
        )}
        <div
          className={[
            fullBleedModule
              ? 'min-w-0 flex-1 p-0'
              : hidePlatformTopbar
                ? 'min-w-0 flex-1 px-4 pb-4 pt-4 transition-[margin] duration-300 md:px-6 md:pb-6'
                : 'min-w-0 flex-1 space-y-6 px-4 pb-4 pt-14 transition-[margin] duration-300 md:px-6 md:pb-6',
            fullBleedModule ? '' : desktopSidebarExpanded ? 'lg:ml-[284px] lg:pt-6' : 'lg:ml-[92px] lg:pt-6',
          ].join(' ')}
        >
          {hidePlatformTopbar || fullBleedModule ? null : <Topbar />}
          <ErrorBoundary>
            <Outlet />
          </ErrorBoundary>
        </div>
      </div>
    </main>
  );
}
