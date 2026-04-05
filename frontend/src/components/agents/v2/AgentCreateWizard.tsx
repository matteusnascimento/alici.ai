import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { AgentIdentityStep } from './AgentIdentityStep';
import { AgentObjectiveStep } from './AgentObjectiveStep';
import { AgentStepLayout } from './AgentStepLayout';
import { createAgentV2 } from '../../../services/agentsV2.service';
import { ApiError } from '../../../services/api';

export function AgentCreateWizard() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [identity, setIdentity] = useState({ nome: '', funcao: 'Atendimento', linguagem: 'pt-BR', tone: 'Consultivo e claro' });
  const [objectives, setObjectives] = useState<string[]>([]);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  function toggle(list: string[], value: string, setter: (value: string[]) => void) {
    setter(list.includes(value) ? list.filter((item) => item !== value) : [...list, value]);
  }

  async function handleNext() {
    if (step === 1 && identity.nome.trim().length < 2) {
      setValidationError('Informe o nome do agente para continuar.');
      return;
    }

    if (step === 2 && objectives.length === 0) {
      setValidationError('Selecione ao menos um objetivo operacional.');
      return;
    }

    setValidationError(null);

    if (step === 1) {
      setStep(2);
      return;
    }

    setSaving(true);
    try {
      const created = await createAgentV2({
        nome: identity.nome,
        funcao: identity.funcao,
        tipo: identity.funcao.toLowerCase().replace(/ /g, '-'),
        linguagem: identity.linguagem,
        tone: identity.tone,
        objectives,
        prompt: `Tom: ${identity.tone}. Objetivos: ${objectives.join(', ')}`,
        ativo: false,
      });

      navigate(`/app/agents/${created.agent.id}/overview?created=1`, {
        state: {
          creationSuccess: true,
          setupPreview: created.setup,
        },
      });
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 405) {
          setValidationError('Nao foi possivel concluir a criacao do agente. Tente novamente em instantes.');
        } else if (err.status === 422) {
          setValidationError('Encontramos um problema ao salvar o objetivo do agente. Revise os dados e tente novamente.');
        } else {
          setValidationError('Nao foi possivel concluir a criacao do agente. Tente novamente em instantes.');
        }
      } else {
        setValidationError('Nao foi possivel concluir a criacao do agente. Tente novamente em instantes.');
      }
      console.error(err);
    } finally {
      setSaving(false);
    }
  }

  const content = {
    1: <AgentIdentityStep data={identity} onChange={(next) => setIdentity((current) => ({ ...current, ...next }))} />,
    2: <AgentObjectiveStep selected={objectives} onToggle={(objective) => toggle(objectives, objective, setObjectives)} />,
  } as Record<number, React.ReactNode>;

  const titles = ['Identidade', 'Objetivo'];

  return (
    <AgentStepLayout
      title={titles[step - 1]}
      subtitle="Finalize a criacao e siga para o onboarding operacional completo no overview"
      step={step}
      total={2}
      onBack={step > 1 ? () => setStep((value) => value - 1) : undefined}
      onNext={saving ? undefined : () => void handleNext()}
      nextLabel={step === 2 ? (saving ? 'Criando...' : 'Continuar') : 'Continuar'}
    >
      {validationError ? (
        <p className="mb-3 rounded-xl border border-rose-300/40 bg-rose-500/10 px-3 py-2 text-sm text-rose-100">
          {validationError}
        </p>
      ) : null}
      {content[step]}
    </AgentStepLayout>
  );
}
