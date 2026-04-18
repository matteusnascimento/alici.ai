import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

import { ThemeProvider, useTheme } from '../contexts/ThemeContext';
import type { AccountPreferences } from '../types/account';

const getAccountPreferences = vi.fn();
const updateAccountPreferences = vi.fn();

vi.mock('../services/settingsAccount.service', () => ({
  getAccountPreferences: (...args: unknown[]) => getAccountPreferences(...args),
  updateAccountPreferences: (...args: unknown[]) => updateAccountPreferences(...args),
}));

const initialPreferences: AccountPreferences = {
  language: 'pt-BR',
  voice: 'alloy',
  theme_mode: 'dark',
  accent_color: 'cyan',
  haptic_feedback: false,
  background_conversation: true,
  autocomplete: true,
  trending: true,
  sequence: false,
  split_mode: false,
};

const updatedPreferences: AccountPreferences = {
  ...initialPreferences,
  language: 'en-US',
  theme_mode: 'light',
  accent_color: 'green',
  split_mode: true,
};

function PreferencesProbe() {
  const { preferences, reloadPreferences, savePreferences } = useTheme();

  return (
    <div>
      <button type="button" onClick={() => void reloadPreferences()}>
        reload
      </button>
      <button type="button" onClick={() => void savePreferences(updatedPreferences)}>
        save
      </button>
      <div data-testid="language">{preferences?.language ?? 'none'}</div>
      <div data-testid="theme">{preferences?.theme_mode ?? 'none'}</div>
      <div data-testid="accent">{preferences?.accent_color ?? 'none'}</div>
    </div>
  );
}

describe('ThemeContext preferences flow', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    document.documentElement.removeAttribute('data-theme');
    document.documentElement.removeAttribute('data-theme-mode');
    document.documentElement.removeAttribute('data-accent');
    document.documentElement.lang = 'pt-BR';
    document.documentElement.classList.remove('dark', 'light');
    document.documentElement.style.removeProperty('--accent-color');

    getAccountPreferences.mockResolvedValue(initialPreferences);
    updateAccountPreferences.mockResolvedValue(updatedPreferences);
  });

  it('carrega do backend, aplica no DOM, salva e reidrata do cache', async () => {
    const user = userEvent.setup();
    const { unmount } = render(
      <ThemeProvider>
        <PreferencesProbe />
      </ThemeProvider>,
    );

    expect(screen.getByTestId('language')).toHaveTextContent('none');

    await user.click(screen.getByRole('button', { name: 'reload' }));

    await waitFor(() => {
      expect(screen.getByTestId('language')).toHaveTextContent('pt-BR');
    });

    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    expect(document.documentElement.getAttribute('data-theme-mode')).toBe('dark');
    expect(document.documentElement.getAttribute('data-accent')).toBe('cyan');
    expect(document.documentElement.lang).toBe('pt-BR');
    expect(document.documentElement.classList.contains('dark')).toBe(true);

    await user.click(screen.getByRole('button', { name: 'save' }));

    await waitFor(() => {
      expect(screen.getByTestId('language')).toHaveTextContent('en-US');
    });

    expect(updateAccountPreferences).toHaveBeenCalledWith(updatedPreferences);
    expect(document.documentElement.getAttribute('data-theme')).toBe('light');
    expect(document.documentElement.getAttribute('data-theme-mode')).toBe('light');
    expect(document.documentElement.getAttribute('data-accent')).toBe('green');
    expect(document.documentElement.lang).toBe('en-US');
    expect(document.documentElement.classList.contains('light')).toBe(true);
    expect(localStorage.getItem('axi_preferences_cache')).toContain('en-US');
    expect(localStorage.getItem('axi_preferences_cache')).toContain('green');

    unmount();
    getAccountPreferences.mockReset();

    render(
      <ThemeProvider>
        <PreferencesProbe />
      </ThemeProvider>,
    );

    await waitFor(() => {
      expect(document.documentElement.getAttribute('data-theme')).toBe('light');
    });

    expect(document.documentElement.getAttribute('data-accent')).toBe('green');
    expect(document.documentElement.lang).toBe('en-US');
  });
});