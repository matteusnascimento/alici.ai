import { create } from "zustand";
import type { KnowledgeDocument } from "@/types/api";

interface KnowledgeState {
  documents: KnowledgeDocument[];
  setDocuments: (documents: KnowledgeDocument[]) => void;
  addDocument: (document: KnowledgeDocument) => void;
  removeDocument: (id: string) => void;
}

export const useKnowledgeStore = create<KnowledgeState>((set) => ({
  documents: [],
  setDocuments: (documents) => set({ documents }),
  addDocument: (document) => set((state) => ({ documents: [document, ...state.documents] })),
  removeDocument: (id) =>
    set((state) => ({ documents: state.documents.filter((doc) => doc.id !== id) }))
}));
