import { Outlet } from 'react-router-dom';

export function MarketingShell() {
  return (
    <div className="flex h-full flex-col overflow-hidden">
      <div className="flex-1 overflow-y-auto">
        <Outlet />
      </div>
    </div>
  );
}
