import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
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
    render(
      <MemoryRouter>
        <RevenueIntelligencePage />
      </MemoryRouter>,
    );

    expect(await screen.findByRole('heading', { name: /^Revenue$/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /^Receita$/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Origem das reservas/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Business Pulse/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Top cidades por receita/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Control Room/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /AXI Assistant/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Plano de Acao/i })).toBeInTheDocument();
    expect(screen.getByText(/Receita no periodo/i)).toBeInTheDocument();
    expect(screen.getAllByText(/Reservas/i).length).toBeGreaterThan(0);
    expect(screen.getByRole('button', { name: /Business Pulse/i })).toBeInTheDocument();
  });
});
