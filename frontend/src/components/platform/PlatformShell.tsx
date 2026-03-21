import { Outlet } from 'react-router-dom';

import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';

export function PlatformShell() {
  return (
    <main className="min-h-screen bg-ink px-4 py-4 md:px-6 md:py-6">
      <div className="mx-auto grid max-w-7xl gap-6 lg:grid-cols-[280px_1fr]">
        <Sidebar />
        <div className="space-y-6">
          <Topbar />
          <Outlet />
        </div>
      </div>
    </main>
  );
}
