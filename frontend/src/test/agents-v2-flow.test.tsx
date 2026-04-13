import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { afterAll, beforeEach, describe, expect, it, vi } from 'vitest';

import { AgentCreateWizard } from '../components/agents/v2/AgentCreateWizard';
import { AgentsMainPage } from '../components/agents/v2/AgentsMainPage';

const listAgentsV2Mock = vi.fn();
const createAgentV2Mock = vi.fn();

vi.mock('../services/agentsV2.service', () => ({
  listAgentsV2: (...args: unknown[]) => listAgentsV2Mock(...args),
  createAgentV2: (...args: unknown[]) => createAgentV2Mock(...args),
  connectAgentBoundChannel: vi.fn(),
  activateAgentV2: vi.fn(),
  duplicateAgentV2: vi.fn(),
  pauseAgentV2: vi.fn(),
}));

describe('Agents v2 flow', () => {
  const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

  beforeEach(() => {
    vi.clearAllMocks();
    listAgentsV2Mock.mockResolvedValue([]);
    createAgentV2Mock.mockResolvedValue({
      agent: {
        id: 99,
        nome: 'Agente Novo',
        funcao: 'Atendimento',
        tipo: 'atendimento',
        linguagem: 'pt-BR',
        prompt: 'Prompt',
        ativo: false,
      },
      setup: {
        progress_percent: 0,
        completed_steps: 0,
        total_steps: 5,
        activation_ready: false,
        summary_message: 'Seu agente ainda precisa de 5 etapa(s) para comecar a operar.',
        recommended_next_step: {
          key: 'channels_connected',
          title: 'Conectar canais',
          description: 'Conecte canais',
          route: '/app/agents/99/channels',
          cta: 'Conectar agora',
        },
        checklist: [],
      },
    });
  });

  afterAll(() => {
    consoleErrorSpy.mockRestore();
  });

  it('renderiza loading e estado vazio na lista de agentes', async () => {
    render(
      <MemoryRouter>
        <AgentsMainPage />
      </MemoryRouter>,
    );

    expect(screen.getByText(/Carregando agentes/i)).toBeInTheDocument();
    expect(await screen.findByText(/Seu primeiro agente comeca aqui/i)).toBeInTheDocument();
  });

  it('bloqueia avanço no wizard sem nome do agente', async () => {
    render(
      <MemoryRouter initialEntries={['/app/agents/create']}>
        <Routes>
          <Route path="/app/agents/create" element={<AgentCreateWizard />} />
        </Routes>
      </MemoryRouter>,
    );

    await userEvent.click(screen.getByRole('button', { name: /Continuar/i }));

    expect(screen.getByText(/Informe o nome do agente para continuar/i)).toBeInTheDocument();
    expect(createAgentV2Mock).not.toHaveBeenCalled();
  });

  it('executa o fluxo de criacao e navega para overview', async () => {
    render(
      <MemoryRouter initialEntries={['/app/agents/create']}>
        <Routes>
          <Route path="/app/agents/create" element={<AgentCreateWizard />} />
          <Route path="/app/agents/:id/overview" element={<div>Overview carregada</div>} />
        </Routes>
      </MemoryRouter>,
    );

    await userEvent.type(screen.getAllByRole('textbox')[0], 'Agente Orion');
    await userEvent.click(screen.getByRole('button', { name: /Continuar/i }));

    await userEvent.click(screen.getByRole('button', { name: /Responder clientes/i }));
    await userEvent.click(screen.getByRole('button', { name: /Continuar/i }));
    await userEvent.click(screen.getByRole('button', { name: /Criar agente/i }));

    await waitFor(() => {
      expect(createAgentV2Mock).toHaveBeenCalledTimes(1);
    });

    expect(await screen.findByText(/Overview carregada/i)).toBeInTheDocument();
  });

  it('mostra estado de loading no submit final', async () => {
    let resolveCreate: (value: any) => void = () => {};
    createAgentV2Mock.mockImplementation(
      () =>
        new Promise((resolve: (value: any) => void) => {
          resolveCreate = resolve;
        }),
    );

    render(
      <MemoryRouter initialEntries={['/app/agents/create']}>
        <Routes>
          <Route path="/app/agents/create" element={<AgentCreateWizard />} />
          <Route path="/app/agents/:id/overview" element={<div>Overview carregada</div>} />
        </Routes>
      </MemoryRouter>,
    );

    await userEvent.type(screen.getAllByRole('textbox')[0], 'Agente Orion');
    await userEvent.click(screen.getByRole('button', { name: /Continuar/i }));
    await userEvent.click(screen.getByRole('button', { name: /Responder clientes/i }));
    await userEvent.click(screen.getByRole('button', { name: /Continuar/i }));
    await userEvent.click(screen.getByRole('button', { name: /Criar agente/i }));

    expect(await screen.findByRole('button', { name: /Criando.../i })).toBeInTheDocument();

    resolveCreate({
      agent: {
        id: 99,
        nome: 'Agente Novo',
        funcao: 'Atendimento',
        tipo: 'atendimento',
        linguagem: 'pt-BR',
        prompt: 'Prompt',
        ativo: false,
      },
      setup: {
        progress_percent: 0,
        completed_steps: 0,
        total_steps: 5,
        activation_ready: false,
        summary_message: 'Seu agente ainda precisa de 5 etapa(s) para comecar a operar.',
        recommended_next_step: {
          key: 'channels_connected',
          title: 'Conectar canais',
          description: 'Conecte canais',
          route: '/app/agents/99/channels',
          cta: 'Conectar agora',
        },
        checklist: [],
      },
    });

    expect(await screen.findByText(/Overview carregada/i)).toBeInTheDocument();
  });

  it('mostra erro amigavel quando submit falha', async () => {
    createAgentV2Mock.mockRejectedValue(new Error('Method Not Allowed'));

    render(
      <MemoryRouter initialEntries={['/app/agents/create']}>
        <Routes>
          <Route path="/app/agents/create" element={<AgentCreateWizard />} />
        </Routes>
      </MemoryRouter>,
    );

    await userEvent.type(screen.getAllByRole('textbox')[0], 'Agente Orion');
    await userEvent.click(screen.getByRole('button', { name: /Continuar/i }));
    await userEvent.click(screen.getByRole('button', { name: /Responder clientes/i }));
    await userEvent.click(screen.getByRole('button', { name: /Continuar/i }));
    await userEvent.click(screen.getByRole('button', { name: /Criar agente/i }));

    expect(await screen.findByText(/Nao foi possivel concluir a criacao do agente/i)).toBeInTheDocument();
  });
});
