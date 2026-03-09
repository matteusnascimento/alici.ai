/**
 * lib/apiClient.ts
 *
 * Central API client configuration for the ALICI platform frontend.
 * Re-exports the shared Axios instance and exposes typed helpers for
 * the v1 research endpoints.
 */
import axios from "axios";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/** Pre-configured Axios instance for v1 API calls */
export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30_000,
  headers: {
    "Content-Type": "application/json",
  },
});

// ---------------------------------------------------------------------------
// Research API helpers
// ---------------------------------------------------------------------------

export interface ResearchRequest {
  query: string;
  user_id: string;
}

export interface ResearchAccepted {
  task_id: string;
  status: "accepted";
}

export interface TaskStatusResponse {
  task_id: string;
  /** "pending" | "processing" | "success" | "failure" */
  status: string;
  result?: Record<string, unknown> | null;
}

/** Submit a deep research job and return the task identifier. */
export async function startResearch(
  payload: ResearchRequest
): Promise<ResearchAccepted> {
  const { data } = await apiClient.post<ResearchAccepted>(
    "/v1/research",
    payload
  );
  return data;
}

/** Poll the status (and optional result) of a research task. */
export async function getTaskStatus(
  taskId: string
): Promise<TaskStatusResponse> {
  const { data } = await apiClient.get<TaskStatusResponse>(
    `/v1/research/${taskId}`
  );
  return data;
}
