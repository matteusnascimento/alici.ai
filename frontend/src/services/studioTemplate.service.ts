import { STUDIO_TEMPLATES } from '../data/studioTemplates';
import type { StudioProjectFromTemplate, StudioTemplate, StudioTemplateDefinition } from '../types/studioTemplate';

const PROJECTS_KEY = 'axi_studio_template_projects';

function canUseStorage() {
  return typeof window !== 'undefined' && typeof window.localStorage !== 'undefined';
}

function readProjects(): StudioProjectFromTemplate[] {
  if (!canUseStorage()) return [];
  try {
    const raw = window.localStorage.getItem(PROJECTS_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeProjects(projects: StudioProjectFromTemplate[]) {
  if (!canUseStorage()) return;
  window.localStorage.setItem(PROJECTS_KEY, JSON.stringify(projects));
}

export function listStudioTemplateDefinitions(): StudioTemplateDefinition[] {
  return STUDIO_TEMPLATES.map((template) => structuredClone(template));
}

export function listStudioTemplates(): StudioTemplate[] {
  return STUDIO_TEMPLATES.map((template) => ({
    ...structuredClone(template),
    layers: structuredClone(template.canvas.layers),
  }));
}

export function getStudioTemplateDefinition(templateId: string | null): StudioTemplateDefinition | null {
  if (!templateId) return null;
  const template = STUDIO_TEMPLATES.find((item) => item.id === templateId);
  return template ? structuredClone(template) : null;
}

export function createProjectFromTemplate(template: StudioTemplateDefinition): StudioProjectFromTemplate {
  const now = new Date().toISOString();
  const fields = template.fields.reduce<Record<string, string>>((acc, field) => {
    acc[field.id] = field.defaultValue;
    return acc;
  }, {});

  return {
    id: `project-${Date.now()}`,
    templateId: template.id,
    name: `${template.name} - novo projeto`,
    type: template.type,
    format: template.format,
    fields,
    canvas: structuredClone(template.canvas),
    selectedEffects: [],
    createdAt: now,
    updatedAt: now,
  };
}

export function listLocalStudioProjects(): StudioProjectFromTemplate[] {
  return readProjects().sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));
}

export function getLocalStudioProject(projectId: string | null): StudioProjectFromTemplate | null {
  if (!projectId) return null;
  return readProjects().find((project) => project.id === projectId) || null;
}

export function saveLocalStudioProject(project: StudioProjectFromTemplate): StudioProjectFromTemplate {
  const saved = { ...project, updatedAt: new Date().toISOString() };
  const projects = readProjects();
  const existingIndex = projects.findIndex((item) => item.id === saved.id);
  if (existingIndex >= 0) {
    projects[existingIndex] = saved;
  } else {
    projects.unshift(saved);
  }
  writeProjects(projects);
  return saved;
}

export function duplicateLocalStudioProject(project: StudioProjectFromTemplate): StudioProjectFromTemplate {
  return saveLocalStudioProject({
    ...structuredClone(project),
    id: `project-${Date.now()}`,
    name: `${project.name} copia`,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  });
}
