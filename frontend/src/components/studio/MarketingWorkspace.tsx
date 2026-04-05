import { useState } from 'react';

interface MarketingWorkspaceProps {
  onNotify: (msg: string) => void;
}

const tabs = ['campaigns', 'copy', 'funnels', 'whatsapp', 'content planning'] as const;

type TabId = (typeof tabs)[number];

export function MarketingWorkspace({ onNotify }: MarketingWorkspaceProps) {
  const [activeTab, setActiveTab] = useState<TabId>('campaigns');

  return (
    <section className="space-y-4 rounded-3xl border border-white/10 bg-white/[0.03] p-5">
      <div className="flex flex-wrap gap-2">
        {tabs.map((tab) => (
          <button
            key={tab}
            type="button"
            onClick={() => setActiveTab(tab)}
            className={[
              'rounded-2xl border px-4 py-2 text-sm capitalize transition',
              tab === activeTab ? 'border-cyan/40 bg-cyan/10 text-cyan' : 'border-white/15 text-slate-200',
            ].join(' ')}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.1fr_1fr]">
        <div className="rounded-2xl border border-white/10 bg-ink/40 p-4">
          <h3 className="font-display text-2xl text-white">Ferramentas de Marketing</h3>
          <p className="mt-2 text-sm text-slate-300">Fluxo integrado para campanhas, copy, funis e WhatsApp em modo operacional.</p>
          <textarea
            className="mt-4 h-36 w-full rounded-2xl border border-white/10 bg-ink/70 px-4 py-3 text-sm text-white outline-none focus:border-cyan"
            defaultValue="Descreva objetivo, publico, oferta e tom para gerar um playbook completo"
          />
          <div className="mt-4 flex gap-3">
            <button
              type="button"
              onClick={() => onNotify(`Playbook ${activeTab} gerado em modo mock.`)}
              className="rounded-2xl bg-sand px-4 py-2 text-sm font-semibold text-ink"
            >
              Gerar
            </button>
            <button
              type="button"
              onClick={() => onNotify('Rascunho salvo em projetos.')}
              className="rounded-2xl border border-cyan/35 bg-cyan/10 px-4 py-2 text-sm text-cyan"
            >
              Salvar draft
            </button>
          </div>
        </div>

        <div className="rounded-2xl border border-white/10 bg-ink/40 p-4">
          <p className="text-xs uppercase tracking-[0.2em] text-cyan">Output</p>
          <div className="mt-3 space-y-3 text-sm text-slate-100">
            <p className="rounded-xl border border-white/10 bg-white/[0.03] p-3">Resumo estrategico do tab {activeTab} com direcionamento comercial.</p>
            <p className="rounded-xl border border-white/10 bg-white/[0.03] p-3">Checklist operacional para execucao em equipe.</p>
            <p className="rounded-xl border border-white/10 bg-white/[0.03] p-3">Sugestoes de CTA e mensagem por estagio da jornada.</p>
          </div>
        </div>
      </div>
    </section>
  );
}
