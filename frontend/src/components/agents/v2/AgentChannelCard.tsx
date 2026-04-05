interface AgentChannelCardProps {
  title: string;
  status: string;
  description: string;
  onConnect: () => void;
  onDisconnect: () => void;
  onSync: () => void;
}

export function AgentChannelCard({ title, status, description, onConnect, onDisconnect, onSync }: AgentChannelCardProps) {
  return (
    <article className="rounded-2xl border border-white/10 bg-white/5 p-4">
      <p className="font-semibold text-white">{title}</p>
      <p className="mt-1 text-xs text-slate-300">{description}</p>
      <p className="mt-2 text-xs text-cyan-200">Status: {status}</p>
      <div className="mt-3 flex gap-2">
        <button type="button" onClick={onConnect} className="rounded-lg border border-cyan-300/40 px-3 py-1 text-xs text-cyan-100">Conectar</button>
        <button type="button" onClick={onDisconnect} className="rounded-lg border border-white/20 px-3 py-1 text-xs text-slate-100">Desconectar</button>
        <button type="button" onClick={onSync} className="rounded-lg border border-white/20 px-3 py-1 text-xs text-slate-100">Sincronizar</button>
      </div>
    </article>
  );
}
