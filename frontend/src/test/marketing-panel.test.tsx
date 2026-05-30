import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { expect, vi } from 'vitest';

import { StudioHomePage } from '../components/studio/v2/StudioHomePage';

const { getStudioOverview } = vi.hoisted(() => ({
  getStudioOverview: vi.fn(),
}));

vi.mock('../services/studio.service', () => ({
  getStudioOverview: () => getStudioOverview(),
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
  beforeEach(() => {
    getStudioOverview.mockResolvedValue({
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
          id: 'caption-campaign',
          label: 'Gerar legenda com CTA',
          description: 'Crie legenda, CTA e hashtags para campanha ativa.',
          route: '/app/studio/caption-generator',
        },
      ],
    });
  });

  it('renderiza a home do Studio com busca, categorias e recentes', async () => {
    render(
      <MemoryRouter>
        <StudioHomePage />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /O que vamos criar hoje/i })).toBeInTheDocument();
    expect(screen.getByRole('textbox', { name: /Buscar no Studio/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /^Templates$/i })).toHaveAttribute('href', '/app/studio/templates');
    expect(screen.getByRole('link', { name: /Video/i })).toHaveAttribute('href', '/app/studio/editor/video?mode=new');
    expect(screen.getByRole('link', { name: /Story/i })).toHaveAttribute('href', '/app/studio/templates?category=Stories');
    expect(screen.getByRole('link', { name: /^Uploads$/i })).toHaveAttribute('href', '/app/studio/assets');
    expect(screen.getByRole('link', { name: /Landing Page/i })).toHaveAttribute('href', '/app/studio/templates?category=Landing%20Pages');
    expect(screen.getAllByRole('link', { name: /Magic Studio/i })[0]).toHaveAttribute('href', '/app/studio/ai-creative');
    expect(screen.getByRole('link', { name: /Poster de lancamento/i })).toHaveAttribute('href', '/app/studio/tools/ad');
  });
});
