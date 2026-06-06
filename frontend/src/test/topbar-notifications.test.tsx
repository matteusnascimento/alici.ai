import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, useLocation } from 'react-router-dom';
import { vi } from 'vitest';

const markNotificationRead = vi.fn();
const markAllNotificationsRead = vi.fn();

vi.mock('../services/notifications.service', () => ({
  listNotifications: () =>
    Promise.resolve([
      {
        id: 1,
        tipo: 'whatsapp',
        titulo: 'Nova mensagem no WhatsApp',
        descricao: 'Juliana Santos respondeu sua cotacao.',
        horario: new Date().toISOString(),
        lida: false,
        destino: '/app/chats',
      },
    ]),
  markNotificationRead: (...args: unknown[]) => markNotificationRead(...args),
  markAllNotificationsRead: (...args: unknown[]) => markAllNotificationsRead(...args),
}));

import { Topbar } from '../components/platform/Topbar';

function LocationProbe() {
  const location = useLocation();
  return <span data-testid="location">{location.pathname}</span>;
}

describe('Topbar notifications', () => {
  it('abre painel operacional sem navegar para preferencias de conta', async () => {
    const user = userEvent.setup();

    render(
      <MemoryRouter initialEntries={['/app/revenue']}>
        <Topbar />
        <LocationProbe />
      </MemoryRouter>,
    );

    await user.click(screen.getByLabelText('Notificacoes'));

    expect(await screen.findByRole('heading', { name: 'Notificacoes' })).toBeInTheDocument();
    expect(screen.getByText('Nova mensagem no WhatsApp')).toBeInTheDocument();
    expect(screen.getByText('Abrir: /app/chats')).toBeInTheDocument();
    await waitFor(() => expect(screen.getByTestId('location')).toHaveTextContent('/app/revenue'));
  });
});
