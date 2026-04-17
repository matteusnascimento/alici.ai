import { useEffect, useState } from 'react';

import {
  createAgentFaqKnowledgeV2,
  createAgentManualKnowledgeV2,
  deleteAgentKnowledgeV2,
  listAgentKnowledgeV2,
  uploadAgentKnowledgeFileV2,
} from '../../services/agentsV2.service';
import type { AgentKnowledgeSource } from '../../types/agentsV2';

export function useAgentKnowledge(agentId: number) {
  const [data, setData] = useState<AgentKnowledgeSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  async function reload() {
    setLoading(true);
    try {
      const result = await listAgentKnowledgeV2(agentId);
      setData(Array.isArray(result) ? result : []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao carregar materiais');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (!agentId) return;
    void reload();
  }, [agentId]);

  async function addFile(file: File, options?: { title?: string; tags?: string; enabled?: boolean }) {
    setSaving(true);
    try {
      const item = await uploadAgentKnowledgeFileV2(agentId, {
        file,
        ...options,
      });
      setData((current) => [item, ...current]);
      return item;
    } finally {
      setSaving(false);
    }
  }

  async function addManual(payload: { title: string; content: string; tags?: string; enabled?: boolean }) {
    setSaving(true);
    try {
      const item = await createAgentManualKnowledgeV2(agentId, payload);
      setData((current) => [item, ...current]);
      return item;
    } finally {
      setSaving(false);
    }
  }

  async function addFaq(payload: { question: string; answer: string; tags?: string; enabled?: boolean }) {
    setSaving(true);
    try {
      const item = await createAgentFaqKnowledgeV2(agentId, payload);
      setData((current) => [item, ...current]);
      return item;
    } finally {
      setSaving(false);
    }
  }

  async function remove(sourceId: number) {
    await deleteAgentKnowledgeV2(agentId, sourceId);
    setData((current) => current.filter((item) => item.id !== sourceId));
  }

  return { data, loading, error, saving, reload, addFile, addManual, addFaq, remove };
}
