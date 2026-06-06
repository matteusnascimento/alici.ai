import { beforeEach, describe, expect, it, vi } from 'vitest';

import {
  connectAgentBoundChannel,
  listAgentBoundChannels,
  listChannelIntegrationAccounts,
  listChannelProviderCatalog,
  testAgentBoundChannel,
} from '../services/agentsV2.service';

const API_BASE = 'http://127.0.0.1:8000/api';

describe('agentsV2 channels service', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
  });

  it('consome rotas de catalogo, contas e bindings corretamente', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValue({
        ok: true,
        status: 200,
        text: async () => '[]',
      } as Response);

    await listChannelProviderCatalog();
    await listChannelIntegrationAccounts();
    await listAgentBoundChannels(42);

    expect(fetchMock).toHaveBeenNthCalledWith(1, `${API_BASE}/integrations`, expect.any(Object));
    expect(fetchMock).toHaveBeenNthCalledWith(2, `${API_BASE}/integrations/accounts`, expect.any(Object));
    expect(fetchMock).toHaveBeenNthCalledWith(3, `${API_BASE}/agents/42/channels`, expect.any(Object));
  });

  it('envia payloads compativeis para connect e test', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValue({
        ok: true,
        status: 200,
        text: async () => '{}',
      } as Response);

    await connectAgentBoundChannel(7, {
      provider: 'whatsapp',
      integration: { external_account_id: 'waba-1', external_account_name: 'Conta AXI' },
      endpoint: { external_channel_id: 'phone-1', channel_name: 'Canal 1' },
    });
    await testAgentBoundChannel(7, 11, 'teste');

    const [, connectOptions] = fetchMock.mock.calls[0];
    const [, testOptions] = fetchMock.mock.calls[1];

    expect(fetchMock).toHaveBeenNthCalledWith(1, `${API_BASE}/agents/7/channels/connect`, expect.any(Object));
    expect(fetchMock).toHaveBeenNthCalledWith(2, `${API_BASE}/agents/7/channels/test`, expect.any(Object));

    expect(typeof (connectOptions as RequestInit).body).toBe('string');
    expect(JSON.parse(String((connectOptions as RequestInit).body))).toMatchObject({
      provider: 'whatsapp',
      integration: { external_account_id: 'waba-1' },
      endpoint: { external_channel_id: 'phone-1' },
    });

    expect(typeof (testOptions as RequestInit).body).toBe('string');
    expect(JSON.parse(String((testOptions as RequestInit).body))).toEqual({ binding_id: 11, message: 'teste' });
  });
});
