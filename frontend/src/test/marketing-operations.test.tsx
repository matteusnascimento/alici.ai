import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi } from 'vitest';

const { listProjects } = vi.hoisted(() => ({
  listProjects: vi.fn(),
}));

vi.mock('../services/marketing.service', () => ({
  listProjects: () => listProjects(),
}));

import { MarketingProjectsPage } from '../components/marketing/MarketingProjectsPage';

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
  });
});
