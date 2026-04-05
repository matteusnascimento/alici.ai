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

  if (loading) return <p className="text-slate-300">Carregando overview...</p>;
  if (error || !data) {
    return (
      <div className="space-y-3 rounded-2xl border border-rose-300/35 bg-rose-500/10 p-4">
        <p className="text-rose-200">{error || 'Falha ao carregar overview'}</p>
        <button type="button" onClick={() => void reload()} className="rounded-xl border border-white/20 px-3 py-2 text-sm text-slate-100">Tentar novamente</button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {showCreationSuccess ? <AgentCreationSuccessState /> : null}
      <AgentOverviewHeader data={data} />
      {activationError ? <p className="rounded-xl border border-rose-300/35 bg-rose-500/10 px-3 py-2 text-sm text-rose-100">{activationError}</p> : null}
      <AgentSetupSummaryBanner message={data.setup.summary_message} />
      <div className="grid gap-4 lg:grid-cols-[1.2fr_1fr]">
        <AgentReadinessCard setup={data.setup} />
        <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
          <p className="text-xs uppercase tracking-[0.18em] text-cyan-300">Ativacao</p>
          <p className="mt-2 text-sm text-slate-200">Ative o agente somente quando o checklist minimo estiver completo.</p>
          <button
            type="button"
            onClick={() => void handleActivate()}
            disabled={!data.setup.activation_ready || activating}
            className="mt-3 rounded-xl bg-cyan px-4 py-2 text-sm font-semibold text-ink disabled:cursor-not-allowed disabled:opacity-50"
          >
            {activating ? 'Ativando...' : 'Ativar agente'}
          </button>
        </div>
      </div>
      <AgentRecommendedNextStepCard step={data.setup.recommended_next_step} />
      <AgentQuickNavigationCards items={data.setup.checklist} />
      <AgentSetupChecklist items={data.setup.checklist} />
      <section className="rounded-2xl border border-white/10 bg-white/5 p-4">
        <p className="font-semibold text-white">Atividade recente</p>
        <div className="mt-3">
          <AgentLogList items={data.historico_de_atividade} />
        </div>
      </section>
    </div>
  );
}
