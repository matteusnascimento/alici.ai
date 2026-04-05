interface AgentSandboxChatProps {
  messages: Array<{ role: 'user' | 'assistant'; text: string }>;
}

export function AgentSandboxChat({ messages }: AgentSandboxChatProps) {
  return (
    <div className="rounded-2xl border border-white/10 bg-black/20 p-3">
      <p className="mb-2 text-xs uppercase tracking-[0.16em] text-slate-400">Sandbox chat</p>
      <div className="space-y-2">
        {messages.map((message, index) => (
          <div key={index} className={`rounded-xl px-3 py-2 text-sm ${message.role === 'assistant' ? 'bg-cyan-500/15 text-cyan-100' : 'bg-white/5 text-slate-200'}`}>
            {message.text}
          </div>
        ))}
      </div>
    </div>
  );
}
