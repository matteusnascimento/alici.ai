interface AgentProgressRingProps {
  value: number;
}

export function AgentProgressRing({ value }: AgentProgressRingProps) {
  const clamped = Math.max(0, Math.min(100, value));

  return (
    <div className="relative h-24 w-24 rounded-full border border-cyan-300/40 p-1">
      <div
        className="h-full w-full rounded-full"
        style={{
          background: `conic-gradient(rgba(34,211,238,0.95) ${clamped * 3.6}deg, rgba(148,163,184,0.2) 0deg)`,
        }}
      >
        <div className="flex h-full w-full items-center justify-center rounded-full bg-slate-950 text-lg font-semibold text-white">{clamped}%</div>
      </div>
    </div>
  );
}
