"use client";

/**
 * hooks/useTaskStatus.ts
 *
 * React hook that polls the ALICI v1 task-status endpoint at a configurable
 * interval until the task reaches a terminal state (success or failure).
 *
 * Usage:
 *   const { status, result, error } = useTaskStatus(taskId);
 */
import { useCallback, useEffect, useRef, useState } from "react";
import { getTaskStatus, TaskStatusResponse } from "@/lib/apiClient";

const TERMINAL_STATUSES = new Set(["success", "failure"]);
const DEFAULT_POLL_INTERVAL_MS = 3_000;

export interface UseTaskStatusOptions {
  /** How often to poll in milliseconds (default: 3000). */
  pollIntervalMs?: number;
  /** Called when the task transitions to a terminal state. */
  onComplete?: (response: TaskStatusResponse) => void;
}

export interface UseTaskStatusResult {
  status: TaskStatusResponse["status"] | null;
  result: TaskStatusResponse["result"];
  error: string | null;
  isLoading: boolean;
}

/**
 * Polls `/v1/research/{taskId}` until the task completes.
 *
 * @param taskId - The task identifier returned by `POST /v1/research`.
 *                 Pass `null` or an empty string to skip polling.
 */
export function useTaskStatus(
  taskId: string | null | undefined,
  options: UseTaskStatusOptions = {}
): UseTaskStatusResult {
  const { pollIntervalMs = DEFAULT_POLL_INTERVAL_MS, onComplete } = options;

  const [status, setStatus] = useState<UseTaskStatusResult["status"]>(null);
  const [result, setResult] = useState<UseTaskStatusResult["result"]>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const onCompleteRef = useRef(onComplete);
  onCompleteRef.current = onComplete;

  const clearPoller = useCallback(() => {
    if (intervalRef.current !== null) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const poll = useCallback(async (id: string) => {
    try {
      const response = await getTaskStatus(id);
      setStatus(response.status);

      if (TERMINAL_STATUSES.has(response.status)) {
        setResult(response.result ?? null);
        setIsLoading(false);
        clearPoller();
        onCompleteRef.current?.(response);
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to fetch task status";
      setError(message);
      setIsLoading(false);
      clearPoller();
    }
  }, [clearPoller]);

  useEffect(() => {
    if (!taskId) return;

    setIsLoading(true);
    setStatus(null);
    setResult(null);
    setError(null);

    let terminated = false;

    const pollOnce = async (id: string) => {
      try {
        const response = await getTaskStatus(id);
        setStatus(response.status);

        if (TERMINAL_STATUSES.has(response.status)) {
          terminated = true;
          setResult(response.result ?? null);
          setIsLoading(false);
          clearPoller();
          onCompleteRef.current?.(response);
        }
      } catch (err) {
        terminated = true;
        const message =
          err instanceof Error ? err.message : "Failed to fetch task status";
        setError(message);
        setIsLoading(false);
        clearPoller();
      }
    };

    // Immediate first poll
    pollOnce(taskId).then(() => {
      // Only start interval polling if task did not reach terminal state immediately
      if (!terminated) {
        intervalRef.current = setInterval(() => poll(taskId), pollIntervalMs);
      }
    });

    return () => {
      clearPoller();
    };
  }, [taskId, pollIntervalMs, poll, clearPoller]);

  return { status, result, error, isLoading };
}
