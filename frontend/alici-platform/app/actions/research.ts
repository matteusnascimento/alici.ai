"use server";

/**
 * app/actions/research.ts
 *
 * Next.js Server Actions for managing deep research tasks.
 *
 * These actions run exclusively on the server and can be imported directly
 * into React Server Components or called from Client Components via the
 * `useTransition` / `startTransition` API.
 */

import { startResearch, getTaskStatus } from "@/lib/apiClient";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface StartResearchState {
  taskId: string | null;
  error: string | null;
}

export interface TaskState {
  taskId: string;
  status: string;
  result: Record<string, unknown> | null | undefined;
  error: string | null;
}

// ---------------------------------------------------------------------------
// Actions
// ---------------------------------------------------------------------------

/**
 * Submit a new deep research job to the ALICI API.
 *
 * @param query   - The user's research question or topic.
 * @param userId  - Identifier of the authenticated user.
 * @returns       An object with the queued `taskId` or an `error` message.
 */
export async function submitResearchAction(
  query: string,
  userId: string
): Promise<StartResearchState> {
  try {
    const response = await startResearch({ query, user_id: userId });
    return { taskId: response.task_id, error: null };
  } catch (err) {
    const message =
      err instanceof Error ? err.message : "Failed to start research task";
    return { taskId: null, error: message };
  }
}

/**
 * Fetch the current status of a previously submitted task.
 *
 * @param taskId - The task identifier returned by `submitResearchAction`.
 * @returns      The current task state including status and result when done.
 */
export async function fetchTaskStatusAction(
  taskId: string
): Promise<TaskState> {
  try {
    const response = await getTaskStatus(taskId);
    return {
      taskId,
      status: response.status,
      result: response.result,
      error: null,
    };
  } catch (err) {
    const message =
      err instanceof Error ? err.message : "Failed to fetch task status";
    return { taskId, status: "unknown", result: null, error: message };
  }
}
