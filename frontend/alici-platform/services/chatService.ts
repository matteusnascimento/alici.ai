import { api } from "@/services/api";

export interface SendMessageInput {
  conversationId?: string;
  message: string;
}

export async function sendMessage(data: SendMessageInput) {
  const response = await api.post("/chat", data);
  return response.data;
}
