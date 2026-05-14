import { apiFetch } from './api';
import type { ChatMessage, ChatSendPayload, ChatSendResponse, Conversation } from '../types/chat';

export function getConversations() {
  return apiFetch<Conversation[]>('/chat/conversations');
}

export function getConversationMessages(conversationId: number) {
  return apiFetch<ChatMessage[]>(`/chat/conversations/${conversationId}/messages`);
}

export function sendMessage(payload: ChatSendPayload) {
  return apiFetch<ChatSendResponse>('/chat/send', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
