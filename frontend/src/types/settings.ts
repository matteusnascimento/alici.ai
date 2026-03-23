export interface Profile {
  name: string;
  username: string;
  email: string;
  phone: string | null;
  plan: string;
}

export interface ProfileUpdate {
  name: string;
  username: string;
  email: string;
  phone: string | null;
}

export interface UserSettings {
  background_conversation: boolean;
  autocomplete: boolean;
  trending: boolean;
  sequence: boolean;
  split_mode: boolean;
  language: string;
  voice: string;
}

export interface AccountData {
  profile: Profile;
  settings: UserSettings;
}
