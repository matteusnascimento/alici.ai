import { useEffect, useMemo, useState } from 'react';

import {
  applyStudioTemplate,
  createStudioProject,
  createStudioVersion,
  duplicateStudioProject,
  exportStudioProject,
  listStudioAssets,
  listStudioProjects,
  listStudioTemplates,
  listStudioVersions,
  saveStudioProject,
} from '../services/studio.service';
import type { StudioAsset, StudioExport, StudioProject, StudioTemplate, StudioVersion } from '../types/studioV2';
import { useToast } from './useToast';

interface UseStudioV2Options {
  defaultType: string;
  defaultTitle: string;
  projectId?: number | null;
  forceNew?: boolean;
}

export const FALLBACK_STUDIO_TEMPLATES: StudioTemplate[] = [
  {
    id: -1,
    user_id: null,
    name: 'Promocao de Produto',
    category: 'Marketing',
    style_tag: '9:16',
    template_data: { project_type: 'video-editor', route: '/app/studio/editor/video?mode=new&template=promo-produto', clips: ['Hook', 'Beneficio', 'Oferta', 'CTA'] },
    preview_url: null,
    is_public: true,
    created_at: new Date(0).toISOString(),
  },
  {
    id: -2,
    user_id: null,
    name: 'Oferta Relampago',
    category: 'Marketing',
    style_tag: 'Reels',
    template_data: { project_type: 'video-editor', route: '/app/studio/editor/video?mode=new&template=oferta-relampago', clips: ['Urgencia', 'Produto', 'Desconto', 'CTA'] },
    preview_url: null,
    is_public: true,
    created_at: new Date(0).toISOString(),
  },
  {
    id: -3,
    user_id: null,
    name: 'Reserva Direta',
    category: 'Hotelaria',
    style_tag: 'Story',
    template_data: { project_type: 'video-editor', route: '/app/studio/editor/video?mode=new&template=reserva-direta', clips: ['Destino', 'Experiencia', 'Quarto', 'Reserva'] },
    preview_url: null,
    is_public: true,
    created_at: new Date(0).toISOString(),
  },
  {
    id: -4,
    user_id: null,
    name: 'Experiencia Premium',
    category: 'Hotelaria',
    style_tag: '9:16',
    template_data: { project_type: 'video-editor', route: '/app/studio/editor/video?mode=new&template=experiencia-premium', clips: ['Ambiente', 'Servico', 'Prova social', 'CTA'] },
    preview_url: null,
    is_public: true,
    created_at: new Date(0).toISOString(),
  },
  {
    id: -5,
    user_id: null,
    name: 'Story Social',
    category: 'Redes Sociais',
    style_tag: 'Story',
    template_data: { project_type: 'video-editor', route: '/app/studio/editor/video?mode=new&template=story-social', clips: ['Abertura', 'Mensagem', 'Sticker', 'CTA'] },
    preview_url: null,
    is_public: true,
    created_at: new Date(0).toISOString(),
  },
  {
    id: -6,
    user_id: null,
    name: 'TikTok / Shorts',
    category: 'Redes Sociais',
    style_tag: 'Shorts',
    template_data: { project_type: 'video-editor', route: '/app/studio/editor/video?mode=new&template=tiktok-shorts', clips: ['Hook rapido', 'Corte dinamico', 'Legenda', 'Loop'] },
    preview_url: null,
    is_public: true,
    created_at: new Date(0).toISOString(),
  },
];

export function useStudioV2({ defaultType, defaultTitle, projectId = null, forceNew = false }: UseStudioV2Options) {
  const { pushToast } = useToast();
  const [projects, setProjects] = useState<StudioProject[]>([]);
  const [assets, setAssets] = useState<StudioAsset[]>([]);
  const [templates, setTemplates] = useState<StudioTemplate[]>([]);
  const [versions, setVersions] = useState<StudioVersion[]>([]);
  const [currentProject, setCurrentProject] = useState<StudioProject | null>(null);
  const [saveState, setSaveState] = useState<'saved' | 'saving' | 'dirty'>('saved');
  const [loading, setLoading] = useState(true);
  const [lastExport, setLastExport] = useState<StudioExport | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function ensureWorkspaceProject() {
    setLoading(true);
    try {
      const [projectsResult, assetsResult, templatesResult] = await Promise.allSettled([
        listStudioProjects(),
        listStudioAssets(),
        listStudioTemplates(),
      ]);
      const safeProjects = projectsResult.status === 'fulfilled' && Array.isArray(projectsResult.value) ? projectsResult.value : [];
      const safeAssets = assetsResult.status === 'fulfilled' && Array.isArray(assetsResult.value) ? assetsResult.value : [];
      const loadedTemplates = templatesResult.status === 'fulfilled' && Array.isArray(templatesResult.value) ? templatesResult.value : [];
      const safeTemplates = loadedTemplates.length > 0 ? loadedTemplates : FALLBACK_STUDIO_TEMPLATES;

      setProjects(safeProjects);
      setAssets(safeAssets);
      setTemplates(safeTemplates);

      let candidate = projectId ? safeProjects.find((item) => item.id === projectId) : null;
      if (!candidate && !forceNew) {
        candidate = safeProjects.find((item) => item.project_type === defaultType);
      }
      if (!candidate) {
        candidate = await createStudioProject({
          project_type: defaultType,
          title: defaultTitle,
          metadata: { mode: defaultType },
          canvas_data: {},
          layers: [],
          timeline_data: {},
          export_settings: { format: 'png' },
        });
        setProjects((current) => [candidate as StudioProject, ...current]);
      }

      setCurrentProject(candidate);
      const loadedVersions = await listStudioVersions(candidate.id);
      setVersions(Array.isArray(loadedVersions) ? loadedVersions : []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao carregar Studio');
      setProjects([]);
      setAssets([]);
      setTemplates([]);
      setVersions([]);
      pushToast('Falha ao carregar workspace do Studio.', 'error');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void ensureWorkspaceProject();
  }, [defaultType, defaultTitle, projectId, forceNew]);

  async function saveProject(patch: Record<string, unknown>) {
    if (!currentProject) return;
    setSaveState('saving');
    try {
      const saved = await saveStudioProject(currentProject.id, patch);
      setCurrentProject(saved);
      setProjects((current) => current.map((item) => (item.id === saved.id ? saved : item)));
      setSaveState('saved');
      setError(null);
      pushToast('Projeto salvo com sucesso.', 'success');
    } catch (err) {
      setSaveState('dirty');
      setError(err instanceof Error ? err.message : 'Falha ao salvar projeto');
      pushToast('Falha ao salvar projeto.', 'error');
    }
  }

  async function duplicateProject() {
    if (!currentProject) return;
    try {
      const duplicate = await duplicateStudioProject(currentProject.id);
      setProjects((current) => [duplicate, ...current]);
      setCurrentProject(duplicate);
      const loadedVersions = await listStudioVersions(duplicate.id);
      setVersions(Array.isArray(loadedVersions) ? loadedVersions : []);
      setError(null);
      pushToast('Projeto duplicado com sucesso.', 'success');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao duplicar projeto');
      pushToast('Falha ao duplicar projeto.', 'error');
    }
  }

  async function saveVersion(label: string, payload: { canvas_data?: Record<string, unknown>; layers?: Array<Record<string, unknown>>; timeline_data?: Record<string, unknown> }) {
    if (!currentProject) return;
    try {
      const version = await createStudioVersion(currentProject.id, {
        label,
        canvas_data: payload.canvas_data,
        layers: payload.layers,
        timeline_data: payload.timeline_data,
      });
      setVersions((current) => [version, ...current]);
      setError(null);
      pushToast('Versao salva.', 'info');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao salvar versao');
      pushToast('Falha ao salvar versao.', 'error');
    }
  }

  async function applyTemplate(templateId: number) {
    if (!currentProject) return;
    try {
      const result = await applyStudioTemplate({ template_id: templateId, project_id: currentProject.id });
      setCurrentProject(result.project);
      setProjects((current) => current.map((item) => (item.id === result.project.id ? result.project : item)));
      setSaveState('dirty');
      setError(null);
      pushToast('Template aplicado ao projeto.', 'success');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao aplicar template');
      pushToast('Falha ao aplicar template.', 'error');
    }
  }

  async function exportProject(format: 'png' | 'jpg' | 'webp' | 'mp4' | 'pdf' | 'zip') {
    if (!currentProject) return;
    try {
      const output = await exportStudioProject(currentProject.id, { export_type: format });
      setLastExport(output);
      setError(null);
      pushToast(`Exportacao ${format.toUpperCase()} concluida.`, 'success');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao exportar projeto');
      pushToast('Falha ao exportar projeto.', 'error');
    }
  }

  const projectName = useMemo(() => currentProject?.title ?? defaultTitle, [currentProject?.title, defaultTitle]);

  return {
    projects,
    assets,
    templates,
    versions,
    currentProject,
    projectName,
    loading,
    saveState,
    lastExport,
    error,
    setSaveState,
    saveProject,
    duplicateProject,
    saveVersion,
    applyTemplate,
    exportProject,
    reload: ensureWorkspaceProject,
  };
}
