export interface Agent {
  id: number;
  user_id: number;
  nome: string;
  funcao: string;
  tipo: string;
  linguagem: string;
  prompt: string;
  whatsapp: string | null;
  instagram: string | null;
  api: string | null;
  outros: string | null;
  outros_nome: string | null;
  ativo: boolean;
  created_at: string;
}

export interface AgentInput {
  nome: string;
  funcao: string;
  tipo: string;
  linguagem: string;
  prompt: string;
  whatsapp?: string;
  instagram?: string;
  api?: string;
  outros?: string;
  outros_nome?: string;
  ativo?: boolean;
}
