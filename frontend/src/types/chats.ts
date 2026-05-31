export interface ChatSummary {
  total: number;
  waiting_human: number;
  with_ai: number;
  closed: number;
  provider_status: 'connected' | 'not_configured';
}

export interface ChatChannel {
  key: 'whatsapp' | 'instagram' | 'messenger' | 'website_chat';
  label: string;
  open_count: number;
  status: 'connected' | 'not_configured' | string;
  credentials_configured: boolean;
  last_sync_at?: string | null;
  last_error?: string | null;
}

export interface OmnichannelConversation {
  id: number;
  customer_id: number;
  customer_name: string;
  channel: string;
  status: string;
  ai_mode: 'ia' | 'humano' | 'hibrido';
  assigned_to?: string | null;
  sales_stage?: string | null;
  source?: string | null;
  campaign_id?: string | null;
  last_message_at?: string | null;
  last_message_preview: string;
  unread_count: number;
  city?: string | null;
  state?: string | null;
  phone?: string | null;
  email?: string | null;
  is_ai_active: boolean;
  is_waiting_human: boolean;
}

export interface OmnichannelMessage {
  id: number;
  conversation_id: number;
  sender_type: 'user' | 'assistant' | 'human' | string;
  channel: string;
  message_type: string;
  content: string;
  delivery_status: string;
  created_at: string;
}

export interface ConversationDetail {
  conversation: OmnichannelConversation;
  messages: OmnichannelMessage[];
}

export interface ChatTeamMember {
  id: number;
  name: string;
  email: string;
  status: 'online' | 'offline' | 'unknown' | string;
  assigned_count: number;
}

export interface ChatTag {
  id: string;
  label: string;
  color: string;
}

export interface CustomerReservation {
  id: number;
  check_in: string;
  check_out: string;
  value: number;
  status: string;
}

export interface CustomerReservationsResponse {
  items: CustomerReservation[];
  source: string;
}
