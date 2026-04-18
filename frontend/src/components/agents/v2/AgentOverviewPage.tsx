import { useMemo, useState } from 'react';
import { useLocation, useParams } from 'react-router-dom';

import { useAgentOverview } from '../../../hooks/agentsV2/useAgentOverview';
import { activateAgentV2 } from '../../../services/agentsV2.service';
import { ApiError } from '../../../services/api';
import { AgentCreationSuccessState } from './AgentCreationSuccessState';
import { AgentLogList } from './AgentLogList';
import { AgentOverviewHeader } from './AgentOverviewHeader';
import { AgentQuickNavigationCards } from './AgentQuickNavigationCards';
import { AgentReadinessCard } from './AgentReadinessCard';
import { AgentRecommendedNextStepCard } from './AgentRecommendedNextStepCard';
import { AgentSetupChecklist } from './AgentSetupChecklist';
import { AgentSetupSummaryBanner } from './AgentSetupSummaryBanner';

export function AgentOverviewPage() {
  const location = useLocation();
  const params = useParams();
  const agentId = Number(params.id || 0);
  const { data, loading, error, reload } = useAgentOverview(agentId);
  const [activationError, setActivationError] = useState<string | null>(null);
  const [activating, setActivating] = useState(false);

  const showCreationSuccess = useMemo(() => {
    const fromState = Boolean((location.state as { creationSuccess?: boolean } | null)?.creationSuccess);
    const fromQuery = new URLSearchParams(location.search).get('created') === '1';
    return fromState || fromQuery;
  }, [location.search, location.state]);

  async function handleActivate() {
    if (!data) return;
    setActivating(true);
    setActivationError(null);
    try {
      await activateAgentV2(data.agent.id);
      await reload();
    } catch (err) {
      if (err instanceof ApiError && err.details && typeof err.details === 'object') {
        const payload = err.details as { message?: string; validation_errors?: string[] };
        const message = payload.message || err.message;
        const errors = payload.validation_errors || [];
        setActivationError(errors.length > 0 ? `${message} (${errors.join(', ')})` : message);
      } else {
        setActivationError(err instanceof Error ? err.message : 'Nao foi possivel ativar o agente.');
      }
    } finally {
      setActivating(false);
    }
  }

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="h-28 animate-pulse rounded-3xl bg-white/5" />
        <div className="grid gap-4 lg:grid-cols-[1.2fr_1fr]">
          <div className="h-36 animate-pulse rounded-3xl bg-white/5" />
          <div className="h-36 animate-pulse rounded-3xl bg-white/5" />
        </div>
        <div className="h-24 animate-pulse rounded-3xl bg-white/5" />
      </div>
    );
  }
  if (error || !data) {
    return (
      <div className="space-y-3 rounded-2xl border border-rose-300/35 bg-rose-500/10 p-5">
        <p className="text-rose-200">{error || 'Falha ao carregar visão geral.'}</p>
        <button type="button" onClick={() => void reload()} className="rounded-xl border border-white/20 px-3 py-2 text-sm text-slate-100 transition hover:bg-white/5">Tentar novamente</button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {showCreationSuccess ? <AgentCreationSuccessState /> : null}
      <AgentOverviewHeader data={data} />
      {activationError ? (
        <div className="rounded-2xl border border-rose-400/25 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">{activationError}</div>
      ) : null}
      <AgentSetupSummaryBanner message={data.setup.summary_message} />
      <div className="grid gap-4 lg:grid-cols-[1.2fr_1fr]">
        <AgentReadinessCard setup={data.setup} />
        <section className="flex flex-col gap-3 rounded-3xl border border-white/10 bg-gradient-to-br from-white/[0.07] to-white/[0.03] p-5">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.22em] text-cyan-400/80">Ativação</p>
            <h3 className="mt-1 font-display text-xl text-white">Publicar agente</h3>
            <p className="mt-1.5 text-sm leading-6 text-slate-400">
              {data.setup.activation_ready
                ? 'Tudo pronto. O agente pode começar a responder nos canais configurados.'
                : 'Complete o checklist abaixo antes de ativar o agente.'}
            </p>
          </div>
          <div className="mt-auto">
            <button
              type="button"
              onClick={() => void handleActivate()}
              disabled={!data.setup.activation_ready || activating}
              className="w-full rounded-2xl bg-cyan py-2.5 text-sm font-semibold text-ink transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {activating ? 'Ativando...' : data.setup.activation_ready ? 'Ativar agente' : 'Setup incompleto'}
            </button>
          </div>
        </section>
      </div>
      <AgentRecommendedNextStepCard step={data.setup.recommended_next_step} />
      <AgentQuickNavigationCards items={data.setup.checklist} />
      <AgentSetupChecklist items={data.setup.checklist} />
      <section className="rounded-2xl border border-white/10 bg-white/[0.04] p-5">
        <p className="font-semibold text-white">Atividade recente</p>
        <div className="mt-3">
          <AgentLogList items={data.historico_de_atividade} />
        </div>
      </section>
    </div>
  );
}
