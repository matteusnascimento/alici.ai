import type { AgentSettings } from '../../../types/agentsV2';

interface AgentSettingsPanelProps {
  settings: AgentSettings;
  onChange: (next: AgentSettings) => void;
  onSave: () => void;
  saving: boolean;
}

export function AgentSettingsPanel({ settings, onChange, onSave, saving }: AgentSettingsPanelProps) {
  return (
    <div className="space-y-4 rounded-3xl border border-white/10 bg-white/5 p-5">
      <div>
        <p className="text-xs uppercase tracking-[0.2em] text-cyan-300">Basico</p>
        <div className="mt-2 grid gap-2 md:grid-cols-2">
          <input value={settings.basic.name} onChange={(event) => onChange({ ...settings, basic: { ...settings.basic, name: event.target.value } })} className="rounded-xl border border-white/10 bg-black/25 px-3 py-2 text-sm text-white" />
          <input value={settings.basic.role} onChange={(event) => onChange({ ...settings, basic: { ...settings.basic, role: event.target.value } })} className="rounded-xl border border-white/10 bg-black/25 px-3 py-2 text-sm text-white" />
          <input value={settings.basic.language} onChange={(event) => onChange({ ...settings, basic: { ...settings.basic, language: event.target.value } })} className="rounded-xl border border-white/10 bg-black/25 px-3 py-2 text-sm text-white" />
          <input value={settings.basic.tone || ''} onChange={(event) => onChange({ ...settings, basic: { ...settings.basic, tone: event.target.value } })} placeholder="Tom" className="rounded-xl border border-white/10 bg-black/25 px-3 py-2 text-sm text-white" />
        </div>
      </div>
      <details className="rounded-2xl border border-white/10 p-3">
        <summary className="cursor-pointer text-sm font-semibold text-white">Configuracoes avancadas</summary>
        <div className="mt-2 space-y-2">
          <textarea value={settings.advanced.instrucoes_principais_do_agente || ''} onChange={(event) => onChange({ ...settings, advanced: { ...settings.advanced, instrucoes_principais_do_agente: event.target.value } })} className="min-h-24 w-full rounded-xl border border-white/10 bg-black/25 px-3 py-2 text-sm text-white" />
          <input value={settings.advanced.modelo || ''} onChange={(event) => onChange({ ...settings, advanced: { ...settings.advanced, modelo: event.target.value } })} placeholder="Modelo" className="w-full rounded-xl border border-white/10 bg-black/25 px-3 py-2 text-sm text-white" />
          <input value={settings.advanced.temperature || ''} onChange={(event) => onChange({ ...settings, advanced: { ...settings.advanced, temperature: event.target.value } })} placeholder="Temperatura" className="w-full rounded-xl border border-white/10 bg-black/25 px-3 py-2 text-sm text-white" />
        </div>
      </details>
      <button type="button" onClick={onSave} disabled={saving} className="rounded-xl bg-cyan px-4 py-2 text-sm font-semibold text-ink">{saving ? 'Salvando...' : 'Salvar configuracoes'}</button>
    </div>
  );
}
