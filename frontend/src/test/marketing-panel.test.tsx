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
    expect(screen.getByRole('heading', { name: /Criacao, edicao e biblioteca visual/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Novo projeto/i })).toHaveAttribute('href', '/app/studio/editor/video?mode=new');
    expect(screen.getByRole('link', { name: /Gerar video IA/i })).toHaveAttribute('href', '/app/studio/editor/video?mode=new&entry=ai-video');
    expect(screen.getByRole('link', { name: /Criar anuncio/i })).toHaveAttribute('href', '/app/studio/tools/ad');
    expect(screen.getAllByRole('link', { name: /Gerar legenda/i })[0]).toHaveAttribute('href', '/app/studio/tools/caption');
    expect(screen.getByRole('link', { name: /Poster de lancamento/i })).toHaveAttribute('href', '/app/studio/tools/ad');
    expect(screen.getByRole('link', { name: /Gerar legenda com CTA/i })).toHaveAttribute('href', '/app/studio/tools/caption');
  });
});
