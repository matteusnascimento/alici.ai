import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi } from 'vitest';

const { createProject, listCampaigns, listMarketingResource, listProjects } = vi.hoisted(() => ({
  createProject: vi.fn(),
  listCampaigns: vi.fn(),
  listMarketingResource: vi.fn(),
  listProjects: vi.fn(),
}));

vi.mock('../services/marketing.service', () => ({
  createProject: (payload: unknown) => createProject(payload),
  listCampaigns: () => listCampaigns(),
  listMarketingResource: (resource: string) => listMarketingResource(resource),
  listProjects: () => listProjects(),
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
    expect(screen.getAllByText('Insights IA').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Sem dados reais').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Campanha real').length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Nenhum plano real nesta etapa/i).length).toBeGreaterThan(0);
    expect(screen.getByRole('link', { name: /Novo Plano/i })).toHaveAttribute('href', '/app/marketing/plans/new');
    expect(screen.getByRole('link', { name: /Nova Campanha/i })).toHaveAttribute('href', '/app/marketing/campaigns/new');
  });

  it('renderiza criacao secundaria com publico, canais, objetivos e AXI Assistant', async () => {
    render(
      <MemoryRouter initialEntries={['/app/marketing/plans/new']}>
        <MarketingPlanningPage />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /Criar Plano de Marketing/i })).toBeInTheDocument();
    expect(screen.getByText('Origem do publico')).toBeInTheDocument();
    expect(screen.getByText('Sao Paulo')).toBeInTheDocument();
    expect(screen.getByText('26-35')).toBeInTheDocument();
    expect(screen.getByText('Instagram')).toBeInTheDocument();
    expect(screen.getByText('Gerar Reservas')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /AXI Assistant/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Abrir AXI Assistant/i })).toHaveAttribute('href', '/app/assistant');
  });
});
