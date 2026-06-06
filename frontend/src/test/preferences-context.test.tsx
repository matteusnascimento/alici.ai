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
  interface_animations: true,
  advanced_visual_effects: true,
  compact_menus: false,
  contextual_tips: true,
  confirm_critical_actions: true,
  open_last_module: true,
  autosave_filters: true,
  keyboard_shortcuts: true,
  show_quick_metrics: true,
  assistant_mode: 'automatico',
  assistant_response_detail: 'normais',
  assistant_tone: 'profissional',
  background_conversation: true,
  autocomplete: true,
  trending: true,
  sequence: false,
  split_mode: false,
};

const updatedPreferences: AccountPreferences = {
  ...initialPreferences,
  language: 'en-US',
  theme_mode: 'midnight',
  accent_color: 'gold',
  interface_animations: false,
  advanced_visual_effects: false,
  compact_menus: true,
  assistant_mode: 'executivo',
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
    document.documentElement.removeAttribute('data-theme-variant');
    document.documentElement.removeAttribute('data-accent');
    document.documentElement.removeAttribute('data-animations');
    document.documentElement.removeAttribute('data-visual-effects');
    document.documentElement.removeAttribute('data-menu-density');
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
    expect(document.documentElement.getAttribute('data-theme-variant')).toBe('dark');
    expect(document.documentElement.getAttribute('data-accent')).toBe('cyan');
    expect(document.documentElement.getAttribute('data-animations')).toBe('on');
    expect(document.documentElement.getAttribute('data-visual-effects')).toBe('advanced');
    expect(document.documentElement.getAttribute('data-menu-density')).toBe('comfortable');
    expect(document.documentElement.style.getPropertyValue('--accent-rgb')).toBe('110 231 249');
    expect(document.documentElement.lang).toBe('pt-BR');
    expect(document.documentElement.classList.contains('dark')).toBe(true);

    await user.click(screen.getByRole('button', { name: 'save' }));

    await waitFor(() => {
      expect(screen.getByTestId('language')).toHaveTextContent('en-US');
    });

    expect(updateAccountPreferences).toHaveBeenCalledWith(updatedPreferences);
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    expect(document.documentElement.getAttribute('data-theme-mode')).toBe('midnight');
    expect(document.documentElement.getAttribute('data-theme-variant')).toBe('midnight');
    expect(document.documentElement.getAttribute('data-accent')).toBe('gold');
    expect(document.documentElement.getAttribute('data-animations')).toBe('off');
    expect(document.documentElement.getAttribute('data-visual-effects')).toBe('standard');
    expect(document.documentElement.getAttribute('data-menu-density')).toBe('compact');
    expect(document.documentElement.style.getPropertyValue('--accent-rgb')).toBe('245 197 66');
    expect(document.documentElement.lang).toBe('en-US');
    expect(document.documentElement.classList.contains('dark')).toBe(true);
    expect(localStorage.getItem('axi_preferences_cache')).toContain('en-US');
    expect(localStorage.getItem('axi_preferences_cache')).toContain('gold');

    unmount();
    getAccountPreferences.mockReset();

    render(
      <ThemeProvider>
        <PreferencesProbe />
      </ThemeProvider>,
    );

    await waitFor(() => {
      expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    });

    expect(document.documentElement.getAttribute('data-accent')).toBe('gold');
    expect(document.documentElement.lang).toBe('en-US');
  });
});
