import type { ReactNode } from 'react';

import { StudioTopbar } from './StudioTopbar';

interface StudioShellProps {
  projectName: string;
  saveState: 'saved' | 'saving' | 'dirty';
  onSave: () => void;
  onExport: () => void;
  onDuplicate?: () => void;
  onBackHome?: () => void;
  center: ReactNode;
  right: ReactNode;
  bottom?: ReactNode;
  leftRail?: ReactNode;
}

export function StudioShell({ projectName, saveState, onSave, onExport, onDuplicate, onBackHome, center, right, bottom, leftRail }: StudioShellProps) {
  return (
    <div className="space-y-4 pb-28">
      <StudioTopbar projectName={projectName} saveState={saveState} onSave={onSave} onExport={onExport} onDuplicate={onDuplicate} onBackHome={onBackHome} />
      <div className="space-y-4">
        <div className="grid gap-5 xl:grid-cols-[minmax(0,1fr)_340px]">
          <div className="min-w-0">{center}</div>
          <div className="min-w-0">{right}</div>
        </div>
        {bottom ? bottom : null}
      </div>
      {leftRail ? (
        <div className="fixed bottom-3 left-4 right-4 z-20 xl:left-[max(1rem,calc((100vw-1400px)/2+1rem))] xl:right-[max(1rem,calc((100vw-1400px)/2+1rem))]">
          {leftRail}
        </div>
      ) : null}
    </div>
  );
}
