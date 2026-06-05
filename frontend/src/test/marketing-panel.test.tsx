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

  it('renderiza a home atual do AXI Studio com atalhos de criacao e ferramentas', async () => {
    render(
      <MemoryRouter>
        <StudioHomePage />
      </MemoryRouter>,
    );

    expect(await screen.findByText(/AXI Studio/i)).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Bora criar bonito/i })).toBeInTheDocument();
    expect(screen.getByText(/Crie videos, posts e campanhas com IA/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Editor unificado/i })).toHaveAttribute('href', '/app/studio/editor');
    expect(screen.getByRole('link', { name: /Editar foto/i })).toHaveAttribute('href', '/app/studio/tools/photo-editor');
    expect(screen.getByRole('link', { name: /AutoCut/i })).toHaveAttribute('href', '/app/studio/editor/video?mode=new&entry=autocut');
    expect(screen.getAllByRole('link', { name: /Gerador de IA/i })[0]).toHaveAttribute('href', '/app/studio/ai-creative');
    expect(screen.getByRole('link', { name: /Legendas/i })).toHaveAttribute('href', '/app/studio/tools/caption');
    expect(screen.getByRole('link', { name: /Poster de lancamento/i })).toHaveAttribute('href', '/app/studio/tools/ad');
  });
});
