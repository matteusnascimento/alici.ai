import { Outlet, useLocation } from 'react-router-dom';
import { useState } from 'react';

import { AppSidebar } from '../layout/AppSidebar';
import { Topbar } from './Topbar';
import { ErrorBoundary } from '../common/ErrorBoundary';

export function PlatformShell() {
  const location = useLocation();
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [desktopSidebarExpanded, setDesktopSidebarExpanded] = useState(false);
  const inStudioEditorMode = location.pathname.startsWith('/app/studio/editor/');

  return (
    <main className="min-h-screen bg-ink">
      <div className="flex min-h-screen">
        {inStudioEditorMode ? null : (
          <AppSidebar
            mobileOpen={mobileSidebarOpen}
            onMobileOpen={() => setMobileSidebarOpen(true)}
            onMobileClose={() => setMobileSidebarOpen(false)}
            onDesktopExpandedChange={setDesktopSidebarExpanded}
          />
        )}
        <div
          className={[
            inStudioEditorMode
              ? 'min-w-0 flex-1 p-0'
              : 'min-w-0 flex-1 space-y-6 px-4 pb-4 pt-14 transition-[margin] duration-300 md:px-6 md:pb-6',
            inStudioEditorMode ? '' : desktopSidebarExpanded ? 'lg:ml-[284px] lg:pt-6' : 'lg:ml-[92px] lg:pt-6',
          ].join(' ')}
        >
          {inStudioEditorMode ? null : <Topbar />}
          <ErrorBoundary>
            <Outlet />
          </ErrorBoundary>
        </div>
      </div>
    </main>
  );
}
