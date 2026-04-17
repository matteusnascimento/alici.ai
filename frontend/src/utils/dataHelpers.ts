/**
 * dataHelpers.ts — blindagem global de dados da API
 *
 * Use estes helpers em qualquer lugar onde dados da API podem
 * chegar como undefined, null, {} ou formato inesperado.
 */

const DEV = import.meta.env.DEV;

/** Garante que um valor é array. Retorna [] para qualquer outro tipo. */
export function ensureArray<T>(value: unknown, fieldName?: string): T[] {
  if (Array.isArray(value)) return value as T[];
  if (DEV && value !== undefined && value !== null) {
    console.warn(`[dataHelpers] ensureArray${fieldName ? ` (${fieldName})` : ''}: esperava array, recebeu`, typeof value, value);
  }
  return [];
}

/**
 * Garante que um valor é objeto. Mescla com fallback para garantir campos obrigatórios.
 * Se value for null/undefined/primitivo, retorna o fallback integralmente.
 */
export function ensureObject<T extends Record<string, unknown>>(value: unknown, fallback: T, fieldName?: string): T {
  if (value !== null && value !== undefined && typeof value === 'object' && !Array.isArray(value)) {
    return { ...fallback, ...(value as Record<string, unknown>) } as T;
  }
  if (DEV && value !== undefined) {
    console.warn(`[dataHelpers] ensureObject${fieldName ? ` (${fieldName})` : ''}: esperava objeto, recebeu`, typeof value, value);
  }
  return { ...fallback };
}

/** Garante número. Retorna 0 para undefined/null/NaN/string. */
export function ensureNumber(value: unknown, fieldName?: string): number {
  if (typeof value === 'number' && !Number.isNaN(value)) return value;
  const parsed = Number(value);
  if (!Number.isNaN(parsed) && value !== null && value !== undefined && value !== '') return parsed;
  if (DEV && value !== undefined && value !== null) {
    console.warn(`[dataHelpers] ensureNumber${fieldName ? ` (${fieldName})` : ''}: esperava número, recebeu`, typeof value, value);
  }
  return 0;
}

/** Garante string. Retorna '' para undefined/null/objeto. */
export function ensureString(value: unknown, fallback = '', fieldName?: string): string {
  if (typeof value === 'string') return value;
  if (DEV && value !== undefined && value !== null) {
    console.warn(`[dataHelpers] ensureString${fieldName ? ` (${fieldName})` : ''}: esperava string, recebeu`, typeof value, value);
  }
  return fallback;
}

// ─── Normalizers por domínio ────────────────────────────────────────────────

import type { RevenueSummary, RevenueRemarketing, RevenueIntelligenceSnapshot, RevenueSeriesResponse } from '../services/revenue.service';

const REVENUE_SUMMARY_DEFAULTS: RevenueSummary = {
  receita_total: 0,
  reservas_fechadas: 0,
  ticket_medio: 0,
  conversao_total: 0,
  leads_recebidos: 0,
  roi_estimado: 0,
  remarketing_recuperado: 0,
  agentes_gerando_receita: 0,
};

const REVENUE_REMARKETING_DEFAULTS: RevenueRemarketing = {
  leads_em_remarketing: 0,
  leads_reativados: 0,
  reservas_recuperadas: 0,
  receita_recuperada: 0,
  taxa_recuperacao: 0,
  campanha_mais_forte: '',
};

export function normalizeRevenueSnapshot(raw: unknown): RevenueIntelligenceSnapshot {
  const obj = ensureObject(raw, {} as Record<string, unknown>, 'RevenueSnapshot');
  return {
    summary: ensureObject(obj.summary, REVENUE_SUMMARY_DEFAULTS, 'summary') as RevenueSummary,
    reservas: ensureArray(obj.reservas, 'reservas'),
    remarketing: ensureObject(obj.remarketing, REVENUE_REMARKETING_DEFAULTS, 'remarketing') as RevenueRemarketing,
    funil: ensureArray(obj.funil, 'funil'),
    receita_por_canal: ensureArray(obj.receita_por_canal, 'receita_por_canal'),
    receita_por_agente: ensureArray(obj.receita_por_agente, 'receita_por_agente'),
    status_oportunidades: ensureArray(obj.status_oportunidades, 'status_oportunidades'),
  };
}

export function normalizeRevenueSeries(raw: unknown): RevenueSeriesResponse {
  const obj = ensureObject(raw, {} as Record<string, unknown>, 'RevenueSeries');
  return {
    days: ensureNumber(obj.days, 'days'),
    granularity: (obj.granularity === 'weekly' ? 'weekly' : 'daily'),
    points: ensureArray(obj.points, 'points'),
  };
}
