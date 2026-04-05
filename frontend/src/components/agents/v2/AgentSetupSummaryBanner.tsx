interface AgentSetupSummaryBannerProps {
  message: string;
}

export function AgentSetupSummaryBanner({ message }: AgentSetupSummaryBannerProps) {
  return (
    <section className="rounded-2xl border border-cyan-300/20 bg-cyan-500/10 px-4 py-3 text-sm text-cyan-100">
      {message}
    </section>
  );
}
