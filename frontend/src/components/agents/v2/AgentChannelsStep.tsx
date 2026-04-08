interface AgentChannelsStepProps {
  selected: string[];
  onToggle: (channel: string) => void;
}

const channels = ['WhatsApp', 'Instagram', 'WebsiteChat', 'Email', 'CRM', 'API', 'Webhook'];

export function AgentChannelsStep({ selected, onToggle }: AgentChannelsStepProps) {
  return (
    <div className="space-y-3">
      <div className="grid gap-2 md:grid-cols-3">
        {channels.map((channel) => {
          const active = selected.includes(channel);
          return (
            <button key={channel} type="button" onClick={() => onToggle(channel)} className={`rounded-xl border px-3 py-3 text-sm ${active ? 'border-cyan-300/40 bg-cyan-500/15 text-cyan-100' : 'border-white/20 text-slate-200'}`}>
              {channel}
            </button>
          );
        })}
      </div>
      {selected.length > 0 ? (
        <div className="grid gap-2 md:grid-cols-2">
          {selected.map((channel) => (
            <div key={channel} className="rounded-2xl border border-white/15 bg-white/5 p-3">
              <p className="font-semibold text-white">{channel}</p>
              <p className="mt-1 text-xs text-slate-300">Conexao em etapa guiada.</p>
              <button type="button" className="mt-2 rounded-lg border border-cyan-300/40 px-3 py-1 text-xs text-cyan-100">Conectar</button>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}
