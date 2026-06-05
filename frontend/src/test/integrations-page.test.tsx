import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { IntegrationsPage } from '../components/integrations/IntegrationsPage';

describe('IntegrationsPage', () => {
  beforeEach(() => {
    localStorage.setItem('axi_token', 'test-token');
  });

  afterEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
  });

  it('mostra detalhe claro quando OAuth retorna 503 por env ausente', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith('/api/integrations')) {
        return new Response(JSON.stringify([]), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.includes('/api/integrations/meta/connect')) {
        return new Response(
          JSON.stringify({
            detail: 'Integração Meta não configurada. Configure META_CLIENT_ID, META_CLIENT_SECRET e META_REDIRECT_URI.',
          }),
          {
            status: 503,
            headers: { 'Content-Type': 'application/json' },
          },
        );
      }
      return new Response(JSON.stringify({ detail: 'Nao encontrado' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      });
    });
    vi.stubGlobal('fetch', fetchMock);

    const user = userEvent.setup();
    render(<IntegrationsPage />);

    expect(await screen.findByRole('heading', { name: /Integracoes/i })).toBeInTheDocument();

    await user.click(screen.getAllByRole('button', { name: /Conectar/i })[0]);

    expect(await screen.findByText(/Integração Meta não configurada/i)).toBeInTheDocument();
  });
});
