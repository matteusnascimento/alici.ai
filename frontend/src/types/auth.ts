export interface User {
  id: number;
  name: string;
  username: string;
  email: string;
  phone: string | null;
  plan: string;
  created_at: string;
}

export interface LoginInput {
  email: string;
  password: string;
}

export interface RegisterInput {
  name: string;
  username: string;
  email: string;
  phone?: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}
