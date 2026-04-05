import { useEffect, useMemo, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

import {
  getProjectById,
  saveProject,
  updateProject,
} from '../services/projectService';
import type { SaveProjectPayload, StudioProject } from '../types/projects';
import type { StudioToolType } from '../types/studio';

interface UseStudioWorkspaceOptions<TInput extends object, TOutput extends object> {
  toolType: StudioToolType;
  route: string;
  emptyInput: TInput;
  emptyOutput: TOutput | null;
}

export function useStudioWorkspace<TInput extends object, TOutput extends object>({
  toolType,
  route,
  emptyInput,
  emptyOutput,
}: UseStudioWorkspaceOptions<TInput, TOutput>) {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  const [input, setInput] = useState<TInput>(emptyInput);
  const [output, setOutput] = useState<TOutput | null>(emptyOutput);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentProject, setCurrentProject] = useState<StudioProject | null>(null);

  const activeProjectId = useMemo(() => searchParams.get('projectId'), [searchParams]);

  useEffect(() => {
    if (!activeProjectId) return;
    const project = getProjectById(activeProjectId);
    if (!project || project.type !== toolType) {
      setError('Projeto invalido para esta ferramenta.');
      return;
    }
    setCurrentProject(project);
    setInput(project.input_data as TInput);
    setOutput(project.output_data as TOutput);
    setError(null);
  }, [activeProjectId, toolType]);

  function resetWorkspace() {
    setInput(emptyInput);
    setOutput(emptyOutput);
    setError(null);
    setCurrentProject(null);
    navigate(route, { replace: true });
  }

  function markError(message: string) {
    setError(message);
  }

  function clearError() {
    setError(null);
  }

  function beginLoading() {
    setLoading(true);
  }

  function endLoading() {
    setLoading(false);
  }

  function saveCurrentProject(title: string, description: string, preview: string) {
    const payload: SaveProjectPayload = {
      type: toolType,
      title,
      description,
      route,
      input_data: input as Record<string, unknown>,
      output_data: (output ?? {}) as Record<string, unknown>,
      preview,
      metadata: { toolType },
    };

    const persisted = currentProject
      ? updateProject(currentProject.id, payload)
      : saveProject(payload);

    if (!persisted) return null;

    setCurrentProject(persisted);
    setSearchParams({ projectId: persisted.id }, { replace: true });
    return persisted;
  }

  return {
    input,
    setInput,
    output,
    setOutput,
    loading,
    beginLoading,
    endLoading,
    error,
    markError,
    clearError,
    currentProject,
    saveCurrentProject,
    resetWorkspace,
  };
}
