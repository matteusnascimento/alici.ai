import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';

import { AgentOverviewPage } from '../components/agents/v2/AgentOverviewPage';

const activateAgentMock = vi.fn();
const reloadMock = vi.fn();
const overviewHookState: { data: any; loading: boolean; error: string | null } = {
  data: {
    agent: {
      id: 10,
      nome: 'AXI Reservas',
      funcao: 'Reservas',
      linguagem: 'pt-BR',
      status: 'draft',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    },
    kpis: {
      conversas_atendidas: 0,
      leads_capturados: 0,
      encaminhamentos_humano: 0,
      tempo_medio_resposta_ms: 0,
    },
    canais_ativos: [],
    historico_de_atividade: [],
    setup: {
      progress_percent: 20,
      completed_steps: 1,
      total_steps: 5,
      activation_ready: false,
      summary_message: 'Seu agente ainda precisa de 4 etapa(s) para comecar a operar.',
      recommended_next_step: {
        key: 'channels_connected',
        title: 'Conectar canais',
        description: 'Conecte um canal para que seu agente possa atuar no seu negocio.',
        route: '/app/agents/10/channels',
        cta: 'Conectar agora',
      },
      checklist: [
        {
          key: 'channels_connected',
          label: 'Conectar canais',
          completed: false,
          detail: 'Nenhum canal conectado',
          route: '/app/agents/10/channels',
          helper_text: 'Escolha onde o agente vai atender.',
        },
        {
          key: 'knowledge_added',
          label: 'Adicionar conhecimento',
          completed: false,
          detail: 'Nenhuma informacao adicionada',
          route: '/app/agents/10/knowledge',
          helper_text: 'Adicione materiais e instrucoes do negocio.',
        },
        {
          key: 'actions_configured',
          label: 'Definir acoes',
          completed: false,
          detail: 'Nenhuma acao configurada',
          route: '/app/agents/10/actions',
          helper_text: 'Habilite automacoes permitidas ao agente.',
        },
        {
          key: 'test_completed',
          label: 'Fazer teste',
          completed: false,
          detail: 'Nenhum teste realizado',
          route: '/app/agents/10/test',
          helper_text: 'Valide respostas no sandbox antes da ativacao.',
        },
        {
          key: 'activation_ready',
          label: 'Ativar agente',
          completed: false,
          detail: 'Configuracao ainda incompleta',
          route: '/app/agents/10/settings',
          helper_text: 'Ative quando os requisitos minimos estiverem completos.',
        },
      ],
    },
  },
  loading: false,
  error: null as string | null,
};

vi.mock('../services/agentsV2.service', () => ({
  activateAgentV2: (...args: unknown[]) => activateAgentMock(...args),
}));

vi.mock('../hooks/agentsV2/useAgentOverview', () => ({
  useAgentOverview: () => ({
    data: overviewHookState.data,
    loading: overviewHookState.loading,
    error: overviewHookState.error,
    reload: (...args: unknown[]) => reloadMock(...args),
  }),
}));

describe('AgentOverviewPage onboarding', () => {
  it('renderiza estado de sucesso, checklist e proximo passo recomendado', async () => {
    overviewHookState.loading = false;
    overviewHookState.error = null;
    render(
      <MemoryRouter initialEntries={['/app/agents/10/overview?created=1']}>
        <Routes>
          <Route path="/app/agents/:id/overview" element={<AgentOverviewPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText(/Seu agente foi criado/i)).toBeInTheDocument();
    expect(screen.getByText(/Checklist de onboarding/i)).toBeInTheDocument();
    expect(screen.getByText(/Proximo passo recomendado/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Conectar agora/i })).toBeInTheDocument();

    const activateButton = screen.getByRole('button', { name: /Ativar agente/i });
    expect(activateButton).toBeDisabled();

    const connectLink = screen.getAllByRole('link', { name: /Conectar canais/i })[0];
    expect(connectLink).toHaveAttribute('href', '/app/agents/10/channels');
  });

  it('mostra estado de loading', async () => {
    overviewHookState.loading = true;
    overviewHookState.error = null;
    overviewHookState.data = null;

    render(
      <MemoryRouter initialEntries={['/app/agents/10/overview']}>
        <Routes>
          <Route path="/app/agents/:id/overview" element={<AgentOverviewPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText(/Carregando overview/i)).toBeInTheDocument();
  });

  it('mostra estado de erro', async () => {
    overviewHookState.loading = false;
    overviewHookState.error = 'Falha ao carregar overview';
    overviewHookState.data = null;

    render(
      <MemoryRouter initialEntries={['/app/agents/10/overview']}>
        <Routes>
          <Route path="/app/agents/:id/overview" element={<AgentOverviewPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText(/Falha ao carregar overview/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Tentar novamente/i })).toBeInTheDocument();
  });
});
