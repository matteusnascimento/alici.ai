interface AgentsFiltersBarProps {
  search: string;
  status: string;
  onSearch: (value: string) => void;
  onStatus: (value: string) => void;
}

export function AgentsFiltersBar({ search, status, onSearch, onStatus }: AgentsFiltersBarProps) {
  return (
    <div className="grid gap-2 rounded-2xl border border-white/10 bg-white/5 p-3 md:grid-cols-[1fr_180px]">
      <input value={search} onChange={(event) => onSearch(event.target.value)} placeholder="Buscar agente por nome ou funcao" className="rounded-xl border border-white/10 bg-black/25 px-3 py-2 text-sm text-white" />
      <select value={status} onChange={(event) => onStatus(event.target.value)} className="rounded-xl border border-white/10 bg-black/25 px-3 py-2 text-sm text-white">
        <option value="all">Todos os status</option>
        <option value="active">Ativos</option>
        <option value="paused">Pausados</option>
      </select>
    </div>
  );
}
