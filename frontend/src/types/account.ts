export interface AccountProfile {
  id: number;
  name: string;
  username: string;
  email: string;
  phone: string | null;
  avatar_url: string | null;
  bio: string | null;
  company: string | null;
  job_title: string | null;
  timezone: string | null;
  language: string;
  email_verified: boolean;
  phone_verified: boolean;
  status: string;
  plan: string;
  created_at: string;
  updated_at: string | null;
  last_login_at: string | null;
}

export interface AccountProfileUpdate {
  name: string;
  username: string;
  email: string;
  phone: string | null;
  avatar_url: string | null;
  bio: string | null;
  company: string | null;
  job_title: string | null;
  timezone: string | null;
  language: string | null;
}

export interface AccountPreferences {
  language: string;
  voice: string;
  theme_mode: string;
  accent_color: string;
  haptic_feedback: boolean;
  background_conversation: boolean;
  autocomplete: boolean;
  trending: boolean;
  sequence: boolean;
  split_mode: boolean;
}

export interface AccountNotifications {
  notifications_enabled: boolean;
  email_notifications: boolean;
  push_notifications: boolean;
  product_updates: boolean;
  marketing_notifications: boolean;
  security_alerts: boolean;
}

export interface AccountIntegration {
  id: number;
  provider: string;
  name: string;
  enabled: boolean;
  status: string;
  updated_at: string | null;
}

export interface AccountSecuritySummary {
  password_last_changed: string | null;
  session_count: number;
  security_alerts: boolean;
}

export interface AccountChangePasswordPayload {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export interface AccountArchivedChatItem {
  id: number;
  title: string;
  archived_at: string | null;
}

export interface AccountArchivedChatList {
  items: AccountArchivedChatItem[];
}

export interface AccountPrivacy {
  archived_chat_visibility: boolean;
  data_portability_supported: boolean;
  account_deletion_supported: boolean;
  notes: string[];
}

export interface AccountHelpInfo {
  app_version: string;
  help_center_url: string;
  report_bug_url: string;
}

export interface AccountLegalInfo {
  terms_url: string;
  privacy_url: string;
}

export interface AccountActionResponse {
  message: string;
}

export interface AccountVerificationChallenge {
  channel: string;
  destination: string;
  expires_at: string;
  message: string;
  preview_code: string | null;
}

export interface AccountVerificationConfirmPayload {
  code: string;
}
