import { afterEach, describe, expect, it, vi } from 'vitest';
import { login, register } from '../services/auth.service';

describe('auth.service', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    localStorage.clear();
  });

  it('uses the backend register contract and normalizes username', async () => {
    const requests: Array<{ url: string; init: RequestInit }> = [];
    vi.stubGlobal(
      'fetch',
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        requests.push({ url: String(input), init: init || {} });
        return new Response(
          JSON.stringify({
            access_token: 'token',
            token_type: 'bearer',
            user: {
              id: 1,
              name: 'Mateus Nascimento dos Santos',
              username: 'matteusnascimento',
              email: 'mateus@example.com',
              phone: '75999309944',
              plan: 'free',
            },
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }),
    );

    await register({
      name: 'Mateus Nascimento dos Santos',
      username: 'Matteus Nascimento',
      email: 'mateus@example.com',
      phone: '75999309944',
      password: 'Senha123',
    });

    expect(requests[0].url).toMatch(/\/api\/auth\/register$/);
    expect(requests[0].init.method).toBe('POST');
    expect(JSON.parse(String(requests[0].init.body))).toEqual({
      name: 'Mateus Nascimento dos Santos',
      username: 'matteusnascimento',
      email: 'mateus@example.com',
      phone: '75999309944',
      password: 'Senha123',
    });

    expect(requests[1].url).toMatch(/\/api\/auth\/login$/);
    expect(requests[1].init.method).toBe('POST');
    expect(JSON.parse(String(requests[1].init.body))).toEqual({
      email: 'mateus@example.com',
      password: 'Senha123',
    });
  });

  it('uses password field when logging in', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () =>
        new Response(
          JSON.stringify({
            access_token: 'token',
            token_type: 'bearer',
            user: {
              id: 1,
              name: 'Mateus',
              username: 'mateus',
              email: 'mateus@example.com',
              plan: 'free',
            },
          }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        ),
      ),
    );

    await login({ email: 'mateus@example.com', password: 'Senha123' });

    const fetchMock = fetch as unknown as ReturnType<typeof vi.fn>;
    const [, init] = fetchMock.mock.calls[0];
    expect(JSON.parse(String(init.body))).toEqual({
      email: 'mateus@example.com',
      password: 'Senha123',
    });
  });
});
