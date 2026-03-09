export interface ApiErrorPayload {
  code: string;
  message: string;
}

export interface ApiEnvelope<T> {
  status: "success" | "error";
  data: T;
  error: ApiErrorPayload | string | null;
}

export function unwrapEnvelope<T>(payload: ApiEnvelope<T> | T): T {
  const maybeEnvelope = payload as ApiEnvelope<T>;
  if (maybeEnvelope && typeof maybeEnvelope === "object" && "status" in maybeEnvelope && "data" in maybeEnvelope) {
    return maybeEnvelope.data;
  }
  return payload as T;
}
