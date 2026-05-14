import { Outlet } from 'react-router-dom';

export function AgentsShell() {
  return (
    <div className="space-y-6">
      <Outlet />
    </div>
  );
}
