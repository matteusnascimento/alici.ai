import { beforeEach, describe, expect, it, vi } from 'vitest';

import {
  connectAgentBoundChannel,
  listAgentBoundChannels,
  listChannelIntegrationAccounts,
  listChannelProviderCatalog,
  testAgentBoundChannel,
} from '../services/agentsV2.service';

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

    expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/integrations$/);
    expect(String(fetchMock.mock.calls[1][0])).toMatch(/\/api\/integrations\/accounts$/);
    expect(String(fetchMock.mock.calls[2][0])).toMatch(/\/api\/agents\/42\/channels$/);
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

    expect(String(fetchMock.mock.calls[0][0])).toMatch(/\/api\/agents\/7\/channels\/connect$/);
    expect(String(fetchMock.mock.calls[1][0])).toMatch(/\/api\/agents\/7\/channels\/test$/);

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
