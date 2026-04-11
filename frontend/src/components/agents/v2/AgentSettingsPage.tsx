import { useState } from 'react';
import { useParams } from 'react-router-dom';

import { useAgentSettings } from '../../../hooks/agentsV2/useAgentSettings';
import { AgentChannelsPage } from './AgentChannelsPage';
import { AgentSettingsPanel } from './AgentSettingsPanel';

type SettingsTab = 'geral' | 'prompt' | 'integracoes' | 'seguranca' | 'logs';

const tabs: Array<{ key: SettingsTab; label: string }> = [
  { key: 'geral', label: 'Geral' },
  { key: 'prompt', label: 'Prompt' },
  { key: 'integracoes', label: 'Integracoes' },
  { key: 'seguranca', label: 'Seguranca' },
  { key: 'logs', label: 'Logs' },
];

export function AgentSettingsPage() {
  const params = useParams();
  const agentId = Number(params.id || 0);
  const { data, loading, saving, error, save, setData } = useAgentSettings(agentId);
  const [activeTab, setActiveTab] = useState<SettingsTab>('geral');

  if (loading) return <p className="text-slate-300">Carregando configuracoes...</p>;
  if (error || !data) return <p className="text-red-300">{error || 'Falha ao carregar configuracoes'}</p>;

  return (
    <div className="space-y-4">
      <header className="rounded-3xl border border-white/10 bg-white/5 p-4">
        <h1 className="font-display text-2xl text-white">Configuracoes do agente</h1>
        <p className="mt-1 text-sm text-slate-300">Painel profissional de governanca e operacao.</p>

        <nav className="mt-4 flex flex-wrap gap-2">
          {tabs.map((tab) => (
            <button
              key={tab.key}
              type="button"
              onClick={() => setActiveTab(tab.key)}
              className={`rounded-xl px-3 py-2 text-xs ${
                activeTab === tab.key
                  ? 'bg-cyan text-ink font-semibold'
                  : 'border border-white/20 text-slate-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </header>

      {activeTab === 'geral' || activeTab === 'prompt' ? (
        <AgentSettingsPanel settings={data} onChange={setData} onSave={() => void save(data)} saving={saving} />
      ) : null}

      {activeTab === 'integracoes' ? <AgentChannelsPage /> : null}

      {activeTab === 'seguranca' ? (
        <section className="rounded-3xl border border-white/10 bg-white/5 p-5">
          <h2 className="text-lg font-semibold text-white">Seguranca</h2>
          <p className="mt-2 text-sm text-slate-300">Tokens e credenciais sensiveis nunca sao expostos no frontend.</p>
        </section>
      ) : null}

      {activeTab === 'logs' ? (
        <section className="rounded-3xl border border-white/10 bg-white/5 p-5">
          <h2 className="text-lg font-semibold text-white">Logs</h2>
          <p className="mt-2 text-sm text-slate-300">Logs estruturados de integracoes estao disponiveis no backend para depuracao.</p>
        </section>
      ) : null}
    </div>
  );
}
