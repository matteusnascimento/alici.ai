import type { SaveProjectPayload, StudioProject } from '../types/projects';

const STORAGE_KEY = 'axi-studio-projects-v1';

function nowIso() {
  return new Date().toISOString();
}

function generateId() {
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function readProjects(): StudioProject[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as StudioProject[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function writeProjects(projects: StudioProject[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(projects));
}

export function getProjects(): StudioProject[] {
  return readProjects().sort((a, b) => b.updated_at.localeCompare(a.updated_at));
}

export function getProjectById(projectId: string): StudioProject | null {
  return getProjects().find((project) => project.id === projectId) ?? null;
}

export function saveProject(payload: SaveProjectPayload): StudioProject {
  const projects = readProjects();
  const project: StudioProject = {
    id: generateId(),
    created_at: nowIso(),
    updated_at: nowIso(),
    metadata: payload.metadata ?? {},
    preview: payload.preview ?? 'Projeto AXI Studio',
    ...payload,
  };
  projects.push(project);
  writeProjects(projects);
  return project;
}

export function updateProject(projectId: string, payload: SaveProjectPayload): StudioProject | null {
  const projects = readProjects();
  const index = projects.findIndex((project) => project.id === projectId);
  if (index < 0) return null;
  const current = projects[index];
  const updated: StudioProject = {
    ...current,
    ...payload,
    updated_at: nowIso(),
  };
  projects[index] = updated;
  writeProjects(projects);
  return updated;
}

export function duplicateProject(projectId: string): StudioProject | null {
  const project = getProjectById(projectId);
  if (!project) return null;
  return saveProject({
    type: project.type,
    title: `${project.title} (copia)`,
    description: project.description,
    route: project.route,
    input_data: project.input_data,
    output_data: project.output_data,
    metadata: project.metadata,
    preview: project.preview,
  });
}

export function deleteProject(projectId: string): boolean {
  const projects = readProjects();
  const filtered = projects.filter((project) => project.id !== projectId);
  if (filtered.length === projects.length) return false;
  writeProjects(filtered);
  return true;
}
