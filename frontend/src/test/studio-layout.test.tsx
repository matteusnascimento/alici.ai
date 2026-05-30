import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { expect, vi } from 'vitest';

import { TemplatesStudioPage } from '../components/studio/v2/TemplatesStudioPage';
import { VideoEditorStudioPage } from '../components/studio/v2/VideoEditorStudioPage';

const studioHook = vi.hoisted(() => ({
  useStudioV2: vi.fn(),
}));

vi.mock('../hooks/useToast', () => ({
  useToast: () => ({
    pushToast: vi.fn(),
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn(),
  }),
}));

vi.mock('../services/studio.service', () => ({
  studioVideoCaptions: vi.fn(),
  studioVideoGenerate: vi.fn(),
  studioVideoVoiceover: vi.fn(),
  uploadStudioAsset: vi.fn(),
}));

vi.mock('../hooks/useStudioV2', async () => {
  const actual = await vi.importActual<typeof import('../hooks/useStudioV2')>('../hooks/useStudioV2');
  return {
    ...actual,
    useStudioV2: studioHook.useStudioV2,
  };
});

function mockStudio() {
  studioHook.useStudioV2.mockReturnValue({
    projects: [],
    assets: [],
    templates: [
      {
        id: 10,
        user_id: null,
        name: 'Reserva Direta',
        category: 'Hotelaria',
        style_tag: '9:16',
        template_data: { project_type: 'video-editor', route: '/app/studio/editor/video?mode=new&template=reserva-direta', clips: ['Hook', 'Quarto', 'CTA'] },
        preview_url: null,
        is_public: true,
        created_at: new Date(0).toISOString(),
      },
    ],
    versions: [],
    currentProject: {
      id: 1,
      user_id: 1,
      project_type: 'video-editor',
      title: 'Campanha teste',
      status: 'draft',
      metadata: {},
      canvas_data: {},
      layers: [],
      timeline_data: {},
      export_settings: {},
      preview_thumbnail_url: null,
      created_at: new Date(0).toISOString(),
      updated_at: new Date(0).toISOString(),
    },
    projectName: 'Campanha teste',
    loading: false,
    saveState: 'saved',
    lastExport: null,
    error: null,
    setSaveState: vi.fn(),
    saveProject: vi.fn(),
    duplicateProject: vi.fn(),
    saveVersion: vi.fn(),
    applyTemplate: vi.fn(),
    exportProject: vi.fn(),
    reload: vi.fn(),
  });
}

describe('Studio layout', () => {
  beforeEach(() => {
    mockStudio();
  });

  it('mantem uma unica topbar no editor e preserva salvar/exportar', () => {
    render(
      <MemoryRouter initialEntries={['/app/studio/editor/video']}>
        <VideoEditorStudioPage />
      </MemoryRouter>,
    );

    expect(screen.getAllByRole('banner')).toHaveLength(1);
    expect(screen.getByRole('button', { name: /Salvar/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Exportar/i })).toBeInTheDocument();
    expect(screen.queryByText(/Editor Unificado/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/AXI Studio Web/i)).not.toBeInTheDocument();
  });

  it('mostra ferramentas principais, efeitos e assets no editor', () => {
    render(
      <MemoryRouter initialEntries={['/app/studio/editor/video']}>
        <VideoEditorStudioPage />
      </MemoryRouter>,
    );

    expect(screen.getByRole('navigation', { name: /Ferramentas do editor/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Modelos/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Uploads/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Texto/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Efeitos/i })).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /Efeitos/i }));
    expect(screen.getByRole('button', { name: /^Fade$/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /^Slide$/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /^Warm$/i })).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /Uploads/i }));
    expect(screen.getByRole('button', { name: /Imagens/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Videos/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Brand Kit/i })).toBeInTheDocument();
  });

  it('exibe templates com formato e acao de uso', () => {
    render(
      <MemoryRouter initialEntries={['/app/studio/templates']}>
        <TemplatesStudioPage />
      </MemoryRouter>,
    );

    expect(screen.getByRole('heading', { name: /Templates para comecar rapido/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Hotelaria/i })).toBeInTheDocument();
    expect(screen.getByText(/Promocao Premium Hotel/i)).toBeInTheDocument();
    expect(screen.getAllByText(/story - 1080x1920/i).length).toBeGreaterThan(0);
    expect(screen.getAllByRole('link', { name: /Usar template/i })[0]).toHaveAttribute('href', '/app/studio/editor/video?mode=new&template=hotel_promo_story_001');
  });
});
