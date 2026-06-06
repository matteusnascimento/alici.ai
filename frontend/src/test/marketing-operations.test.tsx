import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { vi } from 'vitest';

const { createProject, listCampaigns, listMarketingResource, listProjects, publishCampaign } = vi.hoisted(() => ({
  createProject: vi.fn(),
  listCampaigns: vi.fn(),
  listMarketingResource: vi.fn(),
  listProjects: vi.fn(),
  publishCampaign: vi.fn(),
}));

vi.mock('../services/marketing.service', () => ({
  createProject: (payload: unknown) => createProject(payload),
  listCampaigns: () => listCampaigns(),
  listMarketingResource: (resource: string) => listMarketingResource(resource),
  listProjects: () => listProjects(),
  publishCampaign: (id: number, channels: string[]) => publishCampaign(id, channels),
}));

vi.mock('../hooks/useChat', () => ({
  useChat: () => ({
    messages: [],
    loading: false,
    sending: false,
    error: null,
    sendMessage: vi.fn(),
  }),
}));

import { MarketingProjectsPage } from '../components/marketing/MarketingProjectsPage';
import { MarketingPlanningPage } from '../components/marketing/MarketingOperationsPages';

describe('Marketing operations', () => {
  beforeEach(() => {
    listProjects.mockResolvedValue([
      {
        id: 10,
        name: 'Campanha real',
        audience: 'Casais',
        objective: 'Aumentar reservas',
        offer: 'Pacote direto',
        tone: 'premium',
        notes: null,
        created_at: new Date().toISOString(),
      },
    ]);
  });

  it('renderiza dashboard operacional com estados vazios sem dados fake', async () => {
    render(
      <MemoryRouter>
        <MarketingProjectsPage />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: 'Marketing' })).toBeInTheDocument();
    expect(screen.getAllByText('Plano de Acao').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Campanhas').length).toBeGreaterThan(0);
    expect(screen.getAllByText('AXI Assistant').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Sem dados reais').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Campanha real').length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Nenhum plano real nesta etapa/i).length).toBeGreaterThan(0);
    expect(screen.getByRole('link', { name: /Novo Plano/i })).toHaveAttribute('href', '/app/marketing/plans/new');
    expect(screen.getByRole('link', { name: /Nova Campanha/i })).toHaveAttribute('href', '/app/marketing/campaigns/new');
  });

  it('renderiza criacao secundaria com publico, canais, objetivos e AXI Assistant', async () => {
    const user = userEvent.setup();

    render(
      <MemoryRouter initialEntries={['/app/marketing/plans/new']}>
        <MarketingPlanningPage />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /Criar Plano de Marketing/i })).toBeInTheDocument();
    expect(screen.getByText('Marketing Planner')).toBeInTheDocument();
    expect(screen.getByText('Mercado de Origem')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Pesquisar cidade, estado, pais ou regiao/i)).toBeInTheDocument();
    await user.type(screen.getByPlaceholderText(/Pesquisar cidade, estado, pais ou regiao/i), 'Bah');
    expect(screen.getByText('Bahia')).toBeInTheDocument();
    await user.clear(screen.getByPlaceholderText(/Pesquisar cidade, estado, pais ou regiao/i));
    await user.type(screen.getByPlaceholderText(/Pesquisar cidade, estado, pais ou regiao/i), 'Por');
    expect(screen.getByText('Portugal')).toBeInTheDocument();
    expect(screen.getByText('Periodo rapido')).toBeInTheDocument();
    expect(screen.getAllByText('Objetivo principal').length).toBeGreaterThan(0);
    expect(screen.getByText('Objetivos complementares')).toBeInTheDocument();
    expect(screen.getByText('Perfil do cliente')).toBeInTheDocument();
    expect(screen.getByText('25-34')).toBeInTheDocument();
    expect(screen.getByText('Instagram')).toBeInTheDocument();
    expect(screen.getByRole('option', { name: 'Reservas' })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /AXI Assistant/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Abrir AXI Assistant/i })).toHaveAttribute('href', '/app/assistant');
  });
});
