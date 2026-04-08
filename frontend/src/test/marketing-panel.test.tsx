import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { vi } from 'vitest';

import { StudioHomePage } from '../components/studio/v2/StudioHomePage';

vi.mock('../services/studio.service', () => ({
  getStudioOverview: vi.fn(async () => ({
    recent_projects: [
      {
        id: 1,
        title: 'Poster de lancamento',
        project_type: 'poster',
        status: 'draft',
        updated_at: new Date().toISOString(),
        thumbnail_url: null,
      },
    ],
    recent_exports: [
      {
        id: 1,
        project_id: 1,
        project_title: 'Poster de lancamento',
        file_name: 'poster.png',
        export_type: 'png',
        source: 'poster',
        file_url: '/exports/poster.png',
        created_at: new Date().toISOString(),
      },
    ],
    brand_summary: {
      logos_count: 2,
      templates_count: 4,
      palettes_count: 1,
      assets_count: 8,
    },
    suggested_actions: [
      {
        id: 'poster-launch',
        label: 'Criar poster de lancamento',
        description: 'Abra o wizard de poster e gere 3 variacoes.',
        route: '/app/studio/poster',
      },
    ],
  })),
}));

describe('MarketingPanel', () => {
  it('renderiza cards principais do AXI Studio com rotas funcionais', async () => {
    render(
      <MemoryRouter>
        <StudioHomePage />
      </MemoryRouter>,
    );

    expect(await screen.findByText(/Criar Poster/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Novo projeto/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Criar Story/i })).toHaveAttribute('href', '/app/studio/story');
    expect(screen.getByText(/Biblioteca da marca/i)).toBeInTheDocument();
    expect(screen.getByText(/poster.png/i)).toBeInTheDocument();
  });
});
