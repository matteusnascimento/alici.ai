import { fireEvent, render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { beforeEach, describe, expect, it } from 'vitest';

import { StudioHomePage } from '../components/studio/v2/StudioHomePage';
import { TemplatesStudioPage } from '../components/studio/v2/TemplatesStudioPage';
import { UnifiedEditorPage } from '../components/studio/v2/UnifiedEditorPage';
import { getStudioTemplateDefinition, listLocalStudioProjects } from '../services/studioTemplate.service';

describe('AXI Studio template flow', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('Studio Home exibe busca, categorias, templates e projetos recentes', async () => {
    render(
      <MemoryRouter>
        <StudioHomePage />
      </MemoryRouter>,
    );

    expect(await screen.findByLabelText(/Buscar no Studio/i)).toBeInTheDocument();
    expect(screen.getByText('Hotelaria')).toBeInTheDocument();
    expect(screen.getByText('Templates em destaque')).toBeInTheDocument();
    expect(screen.getByText('Criar novo')).toBeInTheDocument();
    expect(screen.getByText('Projetos recentes')).toBeInTheDocument();
    expect(screen.getByText('Uploads recentes')).toBeInTheDocument();
  });

  it('Templates lista badges Free/Premium e link de usar template', () => {
    render(
      <MemoryRouter>
        <TemplatesStudioPage />
      </MemoryRouter>,
    );

    expect(screen.getByText('Templates para comecar rapido')).toBeInTheDocument();
    expect(screen.getAllByText('Usar template').length).toBeGreaterThan(0);
    expect(screen.getAllByText('story - 1080x1920').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Free').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Premium').length).toBeGreaterThan(0);
  });

  it('Editor carrega template, renderiza layers, edita campo, aplica filtro e salva projeto novo', () => {
    const originalTemplate = getStudioTemplateDefinition('hotel_promo_story_001');

    render(
      <MemoryRouter initialEntries={['/app/studio/editor/new?templateId=hotel_promo_story_001']}>
        <Routes>
          <Route path="/app/studio/editor/new" element={<UnifiedEditorPage />} />
          <Route path="/app/studio/editor/:projectId" element={<UnifiedEditorPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getAllByTestId('studio-editor-topbar')).toHaveLength(1);
    expect(screen.getByTestId('studio-template-canvas')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Reserve sua experiencia premium')).toBeInTheDocument();

    fireEvent.change(screen.getByDisplayValue('Reserve sua experiencia premium'), {
      target: { value: 'Nova campanha premium' },
    });
    expect(screen.getByText('Nova campanha premium')).toBeInTheDocument();

    fireEvent.click(screen.getByTitle('Efeitos'));
    fireEvent.click(screen.getByText('Vintage'));
    fireEvent.click(screen.getByText('Salvar'));

    expect(listLocalStudioProjects()).toHaveLength(1);
    expect(getStudioTemplateDefinition('hotel_promo_story_001')?.fields[0].defaultValue).toBe(originalTemplate?.fields[0].defaultValue);
  });
});
