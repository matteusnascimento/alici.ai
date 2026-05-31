import { apiFetch } from './api';
import type {
  ChatChannel,
  ChatSummary,
  ChatTag,
  ChatTeamMember,
  ConversationDetail,
  CustomerReservationsResponse,
  OmnichannelConversation,
} from '../types/chats';

export function getChatSummary() {
  return apiFetch<ChatSummary>('/chats/summary');
}

export function getChatChannels() {
  return apiFetch<ChatChannel[]>('/chats/channels');
}

export function getOmnichannelConversations() {
  return apiFetch<OmnichannelConversation[]>('/chats/conversations');
}

export function getOmnichannelConversation(id: number) {
  return apiFetch<ConversationDetail>(`/chats/conversations/${id}`);
}

export function updateConversationAiMode(id: number, mode: 'ia' | 'humano' | 'hibrido') {
  return apiFetch<OmnichannelConversation>(`/chats/conversations/${id}/ai-mode`, {
    method: 'PATCH',
    body: JSON.stringify({ mode }),
  });
}

export function sendOmnichannelMessage(id: number, content: string) {
  return apiFetch<{ message: unknown }>(`/chats/conversations/${id}/messages`, {
    method: 'POST',
    body: JSON.stringify({ content, message_type: 'text' }),
  });
}

export function getAiSuggestions(id: number) {
  return apiFetch<{ items: string[]; provider?: string | null; source: string }>(`/chats/conversations/${id}/ai-suggestions`, {
    method: 'POST',
  });
}

export function getChatTeam() {
  return apiFetch<ChatTeamMember[]>('/chats/team');
}

export function getChatTags() {
  return apiFetch<ChatTag[]>('/chats/tags');
}

export function getCustomerReservations(customerId: number) {
  return apiFetch<CustomerReservationsResponse>(`/chats/customers/${customerId}/reservations`);
}
