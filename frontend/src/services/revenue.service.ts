import { apiFetch } from './api';

export interface RevenueSummary {
  receita_total: number;
  reservas_fechadas: number;
  ticket_medio: number;
  conversao_total: number;
  leads_recebidos: number;
  roi_estimado: number;
  remarketing_recuperado: number;
  agentes_gerando_receita: number;
}

export interface RevenueReservationItem {
  reserva: string;
  cliente: string;
  canal: string;
  origem: string;
  valor: number;
  status: string;
  agente_responsavel: string;
}

export interface RevenueRemarketing {
  leads_em_remarketing: number;
  leads_reativados: number;
  reservas_recuperadas: number;
  receita_recuperada: number;
  taxa_recuperacao: number;
  campanha_mais_forte: string;
}

export interface RevenueFunnelStep {
  etapa: string;
  total: number;
}

export interface RevenueBreakdownItem {
  label: string;
  valor: number;
}

export interface RevenueOpportunityStatusItem {
  status: string;
  total: number;
}

export interface RevenueOriginDemandItem {
  cidade?: string | null;
  estado?: string | null;
  pais?: string | null;
  canal: string;
  visitantes: number;
  buscas: number;
  cotacoes: number;
  reservas: number;
  receita: number;
  conversao: number;
}

export interface RevenueIntelligenceSnapshot {
  summary: RevenueSummary;
  reservas: RevenueReservationItem[];
  remarketing: RevenueRemarketing;
  funil: RevenueFunnelStep[];
  receita_por_canal: RevenueBreakdownItem[];
  receita_por_agente: RevenueBreakdownItem[];
  status_oportunidades: RevenueOpportunityStatusItem[];
  mapa_origem_demanda: RevenueOriginDemandItem[];
}

export interface RevenueSeriesPoint {
  label: string;
  start_date: string;
  end_date?: string | null;
  receita: number;
  reservas_fechadas: number;
}

export interface RevenueSeriesResponse {
  days: number;
  granularity: 'daily' | 'weekly';
  points: RevenueSeriesPoint[];
}

export function getRevenueIntelligence(days = 30): Promise<RevenueIntelligenceSnapshot> {
  return apiFetch<RevenueIntelligenceSnapshot>(`/revenue/overview?days=${days}`);
}

export function getRevenueSeries(days = 30, granularity: 'daily' | 'weekly' = 'daily'): Promise<RevenueSeriesResponse> {
  return apiFetch<RevenueSeriesResponse>(`/revenue/series?days=${days}&granularity=${granularity}`);
}
