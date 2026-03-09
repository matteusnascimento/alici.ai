import { api } from "@/services/api";
import type { ApiEnvelope, KnowledgeDocumentListData, KnowledgeUploadData, KnowledgeQueryData } from "@/types/api";

/**
 * Function: fetchDocuments
 * Description: List all knowledge documents for the authenticated organization.
 * Returns:
 *   Array of KnowledgeDocument items.
 */
export async function fetchDocuments() {
  const response = await api.get<ApiEnvelope<KnowledgeDocumentListData>>("/knowledge");
  return response.data?.data?.documents ?? [];
}

/**
 * Function: uploadDocument
 * Description: Upload a file to the knowledge base.
 * Parameters:
 *   file: File object to upload.
 *   title: optional document title.
 * Returns:
 *   KnowledgeUploadData with document metadata.
 */
export async function uploadDocument(file: File, title?: string): Promise<KnowledgeUploadData> {
  const form = new FormData();
  form.append("file", file);
  if (title) form.append("title", title);

  const response = await api.post<ApiEnvelope<KnowledgeUploadData>>("/knowledge/upload", form, {
    headers: { "Content-Type": "multipart/form-data" }
  });
  return response.data.data;
}

/**
 * Function: queryKnowledge
 * Description: Query the knowledge base with a natural language question.
 * Parameters:
 *   query: search query string.
 *   top_k: maximum number of references to return (default: 5).
 * Returns:
 *   KnowledgeQueryData with answer and source references.
 */
export async function queryKnowledge(query: string, top_k = 5): Promise<KnowledgeQueryData> {
  const response = await api.post<ApiEnvelope<KnowledgeQueryData>>("/knowledge/query", {
    query,
    top_k
  });
  return response.data.data;
}

/**
 * Function: deleteDocument
 * Description: Delete a knowledge document by id.
 * Parameters:
 *   documentId: id of the document to delete.
 */
export async function deleteDocument(documentId: string): Promise<void> {
  await api.delete(`/knowledge/${documentId}`);
}
