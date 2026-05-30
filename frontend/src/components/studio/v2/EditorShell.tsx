import type { ReactNode } from 'react';

interface EditorShellProps {
  topbar: ReactNode;
  sidebar: ReactNode;
  canvas: ReactNode;
  contextPanel: ReactNode;
  timeline?: ReactNode;
  mode?: 'design' | 'video';
}

export function EditorShell({ topbar, sidebar, canvas, contextPanel, timeline, mode = 'design' }: EditorShellProps) {
  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_14%_0%,rgba(192,38,211,0.18),transparent_34%),radial-gradient(circle_at_84%_0%,rgba(34,211,238,0.12),transparent_32%),linear-gradient(180deg,#050507,#0a0a12)] text-white">
      {topbar}
      <div className="mx-auto grid max-w-[1680px] gap-4 px-4 py-4 lg:grid-cols-[88px_minmax(0,1fr)_360px]">
        <aside className="min-w-0">{sidebar}</aside>
        <section className="min-w-0">
          {canvas}
          {timeline ? (
            <div className={mode === 'video' ? 'mt-4 min-h-[160px] max-h-[220px] overflow-hidden' : 'mt-4'}>
              {timeline}
            </div>
          ) : null}
        </section>
        <aside className="min-w-0">{contextPanel}</aside>
      </div>
    </main>
  );
}
