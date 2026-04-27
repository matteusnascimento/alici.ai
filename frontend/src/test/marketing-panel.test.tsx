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

vi.mock('../hooks/useToast', () => ({
  useToast: () => ({
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn(),
  }),
}));

describe('MarketingPanel', () => {
  it('renderiza a home atual do AXI Studio com atalhos de criacao e ferramentas', async () => {
    render(
      <MemoryRouter>
        <StudioHomePage />
      </MemoryRouter>,
    );

    expect(await screen.findByText(/AXI Studio/i)).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Criar com IA/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Novo v/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Editar foto/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Gerador de IA/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Marketing/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Legendas/i })).toBeInTheDocument();
  });
});
