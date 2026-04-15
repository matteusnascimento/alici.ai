import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';

vi.mock('../services/revenue.service', () => ({
  getRevenueIntelligence: () =>
    Promise.resolve({
      summary: {
        receita_total: 18400,
        reservas_fechadas: 37,
        ticket_medio: 497,
        conversao_total: 17.2,
        leads_recebidos: 214,
        roi_estimado: 3.4,
        remarketing_recuperado: 4800,
        agentes_gerando_receita: 4,
      },
      reservas: [
        {
          reserva: '001',
          cliente: 'Joao',
          canal: 'WhatsApp',
          origem: 'Campanha verao',
          valor: 680,
          status: 'Fechada',
          agente_responsavel: 'Agente Hotel',
        },
      ],
      remarketing: {
        leads_em_remarketing: 82,
        leads_reativados: 21,
        reservas_recuperadas: 9,
        receita_recuperada: 3950,
        taxa_recuperacao: 10.9,
        campanha_mais_forte: 'Reativacao Abril',
      },
      funil: [
        { etapa: 'Leads captados', total: 420 },
        { etapa: 'Leads qualificados', total: 210 },
      ],
      receita_por_canal: [{ label: 'WhatsApp', valor: 7200 }],
      receita_por_agente: [{ label: 'Agente Atendimento Hotel', valor: 8400 }],
      status_oportunidades: [{ status: 'Fechado', total: 23 }],
    }),
  getRevenueSeries: () =>
    Promise.resolve({
      days: 30,
      granularity: 'daily',
      points: [{ label: '14/04', start_date: '2026-04-14', end_date: null, receita: 1840, reservas_fechadas: 3 }],
    }),
}));

import { RevenueIntelligencePage } from '../components/revenue/RevenueIntelligencePage';

describe('RevenueIntelligencePage', () => {
  it('renderiza blocos principais de receita e conversao', async () => {
    render(<RevenueIntelligencePage />);

    expect(await screen.findByRole('heading', { name: /Financeiro e Conversao/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Reservas fechadas/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Remarketing/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Funil comercial/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Receita por canal/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Receita por agente/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Receita historica/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /7 dias/i })).toBeInTheDocument();
  });
});
