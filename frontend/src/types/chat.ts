export interface Conversation {
  id: number;
  user_id: number;
  title: string;
  created_at: string;
}

export interface ChatMessage {
  id: number;
  conversation_id: number;
  role: 'user' | 'assistant';
  text: string;
  created_at: string;
}

export interface ChatSendPayload {
  text: string;
  conversation_id?: number;
  context?: string;
}

export interface ChatSendResponse {
  conversation: Conversation;
  user_message: ChatMessage;
  assistant_message: ChatMessage;
}
