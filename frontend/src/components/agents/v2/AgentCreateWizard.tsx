import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import { AgentIdentityStep } from './AgentIdentityStep';
import { AgentObjectiveStep } from './AgentObjectiveStep';
import { AgentStepLayout } from './AgentStepLayout';
import { AgentChannelsStep } from './AgentChannelsStep';
import { connectAgentBoundChannel, createAgentV2 } from '../../../services/agentsV2.service';
import { ApiError } from '../../../services/api';

const providerMap: Record<string, string> = {
  WhatsApp: 'whatsapp',
  Instagram: 'instagram',
  WebsiteChat: 'website_chat',
  API: 'api',
  Webhook: 'webhook',
};

const knowledgeOptions = ['Upload de arquivos', 'FAQ', 'Conteudo manual', 'Pular por enquanto'];
const actionOptions = [
  'Responder perguntas',
  'Capturar lead',
  'Consultar disponibilidade',
  'Gerar orcamento',
  'Transferir para humano',
  'Registrar interesse',
  'Criar reserva',
  'Acao personalizada',
];

export function AgentCreateWizard() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [identity, setIdentity] = useState({
    nome: '',
    funcao: 'Atendimento',
    linguagem: 'pt-BR',
    tone: 'Consultivo e claro',
    descricao: '',
  });
  const [objectives, setObjectives] = useState<string[]>([]);
  const [channels, setChannels] = useState<string[]>([]);
  const [knowledge, setKnowledge] = useState<string[]>([]);
  const [allowedActions, setAllowedActions] = useState<string[]>([]);
  const [testMessage, setTestMessage] = useState('');
  const [testPreview, setTestPreview] = useState<string | null>(null);
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

    if (step === 5 && allowedActions.length === 0) {
      setValidationError('Selecione ao menos uma acao permitida para o agente.');
      return;
    }

    if (step === 6 && testMessage.trim().length < 5) {
      setValidationError('Digite uma pergunta de teste para validar o comportamento do agente.');
      return;
    }

    setValidationError(null);

    if (step < 7) {
      if (step === 6) {
        setTestPreview(
          `Simulacao: "${testMessage}"\n\nResposta esperada no tom ${identity.tone.toLowerCase()} com foco em ${
            objectives.join(', ') || 'atendimento'
          }.`,
        );
      }
      setStep((value) => value + 1);
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
        prompt: [
          `Descricao: ${identity.descricao || 'Agente para operacao de atendimento e crescimento.'}`,
          `Tom: ${identity.tone}`,
          `Objetivos: ${objectives.join(', ')}`,
          `Acoes permitidas: ${allowedActions.join(', ')}`,
          `Conhecimento inicial: ${knowledge.join(', ') || 'Nao definido'}`,
        ].join(' | '),
        ativo: false,
      });

      // Vincula conexões ao agent_id recém criado
      await Promise.all(
        channels.map(async (channelName) => {
          const provider = providerMap[channelName];
          if (!provider) return;
          await connectAgentBoundChannel(created.agent.id, {
            provider,
            integration: {
              external_account_name: `${provider}-account`,
              metadata: { source: 'agent_create_wizard' },
            },
            endpoint: {
              channel_name: `${provider}-channel`,
            },
          });
        }),
      );

      navigate(`/app/agents/${created.agent.id}/overview?created=1`, {
        state: {
          creationSuccess: true,
          setupPreview: created.setup,
          setupSelections: {
            identity,
            objectives,
            channels,
            knowledge,
            actions: allowedActions,
            quickTest: testMessage,
          },
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

  function renderKnowledgeStep() {
    return (
      <div className="grid gap-3 md:grid-cols-2">
        {knowledgeOptions.map((item) => {
          const active = knowledge.includes(item);
          return (
            <button
              key={item}
              type="button"
              onClick={() => toggle(knowledge, item, setKnowledge)}
              className={`rounded-2xl border p-4 text-left ${active ? 'border-cyan-300/40 bg-cyan-500/15 text-cyan-100' : 'border-white/15 bg-white/5 text-slate-100'}`}
            >
              <p className="font-semibold">{item}</p>
              <p className="mt-1 text-xs opacity-80">Defina como o agente aprende e consulta informacoes.</p>
            </button>
          );
        })}
      </div>
    );
  }

  function renderActionsStep() {
    return (
      <div className="grid gap-3 md:grid-cols-2">
        {actionOptions.map((item) => {
          const active = allowedActions.includes(item);
          return (
            <button
              key={item}
              type="button"
              onClick={() => toggle(allowedActions, item, setAllowedActions)}
              className={`rounded-2xl border p-4 text-left ${active ? 'border-cyan-300/40 bg-cyan-500/15 text-cyan-100' : 'border-white/15 bg-white/5 text-slate-100'}`}
            >
              <p className="font-semibold">{item}</p>
              <p className="mt-1 text-xs opacity-80">Controle operacional permitido para o agente.</p>
            </button>
          );
        })}
      </div>
    );
  }

  function renderQuickTestStep() {
    return (
      <div className="space-y-3">
        <p className="text-sm text-slate-300">
          Teste rapido para validar comportamento antes de publicar. Digite uma pergunta real de cliente.
        </p>
        <textarea
          value={testMessage}
          onChange={(event) => setTestMessage(event.target.value)}
          rows={4}
          placeholder="Ex: Qual o valor da hospedagem para este fim de semana?"
          className="w-full rounded-2xl border border-white/15 bg-white/5 px-3 py-3 text-sm text-white placeholder:text-slate-500"
        />
        {testPreview ? (
          <div className="rounded-2xl border border-cyan-300/30 bg-cyan-500/10 px-3 py-3 text-sm text-cyan-100 whitespace-pre-line">
            {testPreview}
          </div>
        ) : null}
      </div>
    );
  }

  function renderReviewStep() {
    return (
      <div className="grid gap-3 md:grid-cols-2">
        <div className="rounded-2xl border border-white/15 bg-white/5 p-3">
          <p className="text-xs uppercase tracking-[0.15em] text-cyan-200">Identidade</p>
          <p className="mt-1 text-sm text-white">{identity.nome}</p>
          <p className="text-xs text-slate-300">{identity.funcao} · {identity.linguagem}</p>
          <p className="mt-1 text-xs text-slate-400">{identity.tone}</p>
        </div>
        <div className="rounded-2xl border border-white/15 bg-white/5 p-3">
          <p className="text-xs uppercase tracking-[0.15em] text-cyan-200">Objetivos</p>
          <p className="mt-1 text-sm text-white">{objectives.join(', ') || 'Nao definido'}</p>
        </div>
        <div className="rounded-2xl border border-white/15 bg-white/5 p-3">
          <p className="text-xs uppercase tracking-[0.15em] text-cyan-200">Canais</p>
          <p className="mt-1 text-sm text-white">{channels.join(', ') || 'Nenhum por enquanto'}</p>
        </div>
        <div className="rounded-2xl border border-white/15 bg-white/5 p-3">
          <p className="text-xs uppercase tracking-[0.15em] text-cyan-200">Conhecimento</p>
          <p className="mt-1 text-sm text-white">{knowledge.join(', ') || 'Pular por enquanto'}</p>
        </div>
        <div className="rounded-2xl border border-white/15 bg-white/5 p-3 md:col-span-2">
          <p className="text-xs uppercase tracking-[0.15em] text-cyan-200">Acoes permitidas</p>
          <p className="mt-1 text-sm text-white">{allowedActions.join(', ') || 'Nao definido'}</p>
          <p className="mt-1 text-xs text-slate-400">Prontidao operacional: {allowedActions.length > 0 ? 'base pronta para ativacao' : 'requer ajustes'}.</p>
        </div>
      </div>
    );
  }

  const content = {
    1: (
      <div className="space-y-3">
        <AgentIdentityStep data={identity} onChange={(next) => setIdentity((current) => ({ ...current, ...next }))} />
        <textarea
          value={identity.descricao}
          onChange={(event) => setIdentity((current) => ({ ...current, descricao: event.target.value }))}
          rows={3}
          placeholder="Descricao curta da funcao do agente"
          className="w-full rounded-2xl border border-white/15 bg-white/5 px-3 py-3 text-sm text-white placeholder:text-slate-500"
        />
      </div>
    ),
    2: <AgentObjectiveStep selected={objectives} onToggle={(objective) => toggle(objectives, objective, setObjectives)} />,
    3: <AgentChannelsStep selected={channels} onToggle={(channel) => toggle(channels, channel, setChannels)} />,
    4: renderKnowledgeStep(),
    5: renderActionsStep(),
    6: renderQuickTestStep(),
    7: renderReviewStep(),
  } as Record<number, React.ReactNode>;

  const titles = [
    'Identidade',
    'Objetivo',
    'Canais',
    'Conhecimento',
    'Acoes permitidas',
    'Teste rapido',
    'Revisao final',
  ];

  return (
    <AgentStepLayout
      title={titles[step - 1]}
      subtitle="Fluxo guiado de criacao. Ajuste tudo aqui e siga para o workspace operacional apos publicar."
      step={step}
      total={7}
      onBack={step > 1 ? () => setStep((value) => value - 1) : undefined}
      onNext={saving ? undefined : () => void handleNext()}
      nextLabel={step === 7 ? (saving ? 'Publicando...' : 'Publicar agente') : 'Continuar'}
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
