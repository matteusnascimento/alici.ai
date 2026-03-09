"use client";

import { useEffect, useState } from "react";
import { fetchDocuments } from "@/features/knowledge/services/knowledgeService";
import { useKnowledgeStore } from "@/features/knowledge/store/knowledgeStore";

/**
 * Hook: useKnowledge
 * Description: Load knowledge documents for the authenticated organization.
 * Follows the standard loading / error / data pattern.
 */
export function useKnowledge() {
  const { documents, setDocuments } = useKnowledgeStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const list = await fetchDocuments();
        if (active) setDocuments(list);
      } catch {
        if (active) setError("Failed to load knowledge documents");
      } finally {
        if (active) setLoading(false);
      }
    }

    void load();
    return () => {
      active = false;
    };
  }, [setDocuments]);

  return { loading, error, data: documents, documents };
}
