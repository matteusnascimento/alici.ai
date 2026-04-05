import { Outlet } from 'react-router-dom';
import { useState } from 'react';

import { AppSidebar } from '../layout/AppSidebar';
import { Topbar } from './Topbar';

export function PlatformShell() {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [desktopSidebarExpanded, setDesktopSidebarExpanded] = useState(false);

  return (
    <main className="min-h-screen bg-ink">
      <div className="flex min-h-screen">
        <AppSidebar
          mobileOpen={mobileSidebarOpen}
          onMobileOpen={() => setMobileSidebarOpen(true)}
          onMobileClose={() => setMobileSidebarOpen(false)}
          onDesktopExpandedChange={setDesktopSidebarExpanded}
        />
        <div
          className={[
            'min-w-0 flex-1 space-y-6 px-4 pb-4 pt-14 transition-[margin] duration-300 md:px-6 md:pb-6',
            desktopSidebarExpanded ? 'lg:ml-[282px] lg:pt-6' : 'lg:ml-[88px] lg:pt-6',
          ].join(' ')}
        >
          <Topbar />
          <Outlet />
        </div>
      </div>
    </main>
  );
}
