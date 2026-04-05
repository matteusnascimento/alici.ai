import type { ReactNode } from 'react';

import { StudioSidebar } from './StudioSidebar';
import { StudioTopbar } from './StudioTopbar';

interface StudioShellProps {
  projectName: string;
  saveState: 'saved' | 'saving' | 'dirty';
  onSave: () => void;
  onExport: () => void;
  center: ReactNode;
  right: ReactNode;
  bottom: ReactNode;
  leftRail?: ReactNode;
}

export function StudioShell({ projectName, saveState, onSave, onExport, center, right, bottom, leftRail }: StudioShellProps) {
  return (
    <div className="space-y-4">
      <StudioTopbar projectName={projectName} saveState={saveState} onSave={onSave} onExport={onExport} />
      <div className="grid gap-4 xl:grid-cols-[260px_1fr]">
        <StudioSidebar />
        <div className="space-y-4">
          <div className="grid gap-4 lg:grid-cols-[72px_1fr_320px]">
            <div>{leftRail}</div>
            <div>{center}</div>
            <div>{right}</div>
          </div>
          {bottom}
        </div>
      </div>
    </div>
  );
}
