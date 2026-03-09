import { api } from "@/services/api";
import { getAccessToken } from "@/services/authSession";
import type { ApiEnvelope } from "@/types/api";

export interface SendMessageInput {
  conversationId?: string;
  message: string;
  agentId?: string;
}

export interface ConversationItem {
  id: string;
  title: string;
  last_message_at?: string;
  created_at?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at?: string;
}

interface CreateConversationResponse {
  id: string;
  title: string;
  created_at?: string;
}

type StreamChunkHandler = (chunk: string) => void;

type StreamDoneHandler = () => void;

type StreamErrorHandler = (error: Error) => void;

export async function sendMessage(data: SendMessageInput) {
  /**
   * Function: sendMessage
   * Description: Send a chat message using the standard non-streaming endpoint.
   * Parameters:
   *   data: message content and optional conversation id.
   * Returns:
   *   Backend response payload.
   */
  const response = await api.post<ApiEnvelope<Record<string, unknown>>>("/chat/message", data);
  return response.data?.data ?? {};
}

export async function getConversations(): Promise<ConversationItem[]> {
  /**
   * Function: getConversations
   * Description: Fetch conversation headers for the authenticated user.
   * Parameters:
   * Returns:
   *   Array of conversation metadata.
   */
  const response = await api.get<ApiEnvelope<{ history: ConversationItem[] }>>("/chat/conversations");
  return response.data?.data?.history ?? [];
}

export async function getConversationMessages(conversationId: string): Promise<ChatMessage[]> {
  /**
   * Function: getConversationMessages
   * Description: Fetch all messages for a conversation id.
   * Parameters:
   *   conversationId: conversation identifier.
   * Returns:
   *   Array of messages.
   */
  const response = await api.get<ApiEnvelope<{ messages: ChatMessage[] }>>(
    `/chat/conversations/${conversationId}/messages`
  );
  return response.data?.data?.messages ?? [];
}

export async function createConversation(title = "New conversation"): Promise<CreateConversationResponse> {
  /**
   * Function: createConversation
   * Description: Create a new conversation shell in backend.
   * Parameters:
   *   title: optional conversation title.
   * Returns:
   *   Created conversation summary.
   */
  const response = await api.post<ApiEnvelope<{ conversation: CreateConversationResponse }>>("/conversations", {
    title
  });
  const conversation = response.data?.data?.conversation;
  if (!conversation?.id) {
    throw new Error("Invalid create conversation response");
  }
  return conversation;
}

export async function streamMessage(
  data: SendMessageInput,
  handlers: {
    onChunk: StreamChunkHandler;
    onDone?: StreamDoneHandler;
    onError?: StreamErrorHandler;
  }
): Promise<void> {
  /**
   * Function: streamMessage
   * Description: Send a message to the streaming endpoint and emit response chunks incrementally.
   * Parameters:
   *   data: message payload.
   *   handlers: stream lifecycle callbacks.
   * Returns:
   *   Promise resolved after stream completion.
   */
  const baseURL = api.defaults.baseURL ?? "";
  const token = getAccessToken();

  const response = await fetch(`${baseURL}/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    body: JSON.stringify({
      message: data.message,
      conversation_id: data.conversationId,
      ...(data.agentId ? { agent_id: data.agentId } : {})
    })
  });

  if (!response.ok || !response.body) {
    const error = new Error("Streaming request failed");
    handlers.onError?.(error);
    throw error;
  }

  const decoder = new TextDecoder();
  const reader = response.body.getReader();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split("\n\n");
      buffer = events.pop() ?? "";

      for (const event of events) {
        const line = event
          .split("\n")
          .find((entry) => entry.startsWith("data:"));

        if (!line) continue;

        const payload = line.slice(5).trim();
        if (payload === "[DONE]") {
          handlers.onDone?.();
          return;
        }

        try {
          const parsed = JSON.parse(payload) as { data?: { chunk?: string } };
          const chunk = parsed?.data?.chunk ?? "";
          if (chunk) handlers.onChunk(chunk);
        } catch {
          // Ignore malformed SSE chunks and continue stream processing.
        }
      }
    }

    handlers.onDone?.();
  } catch (error) {
    const streamError = error instanceof Error ? error : new Error("Unknown stream error");
    handlers.onError?.(streamError);
    throw streamError;
  } finally {
    reader.releaseLock();
  }
}
