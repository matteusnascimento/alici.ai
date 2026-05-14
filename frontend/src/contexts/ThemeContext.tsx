import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

import { getAccountPreferences, updateAccountPreferences } from '../services/settingsAccount.service';
import { getColorRgbTriplet, getColorValue } from '../utils/colorMap';
import type { AccountPreferences } from '../types/account';

interface ThemeContextType {
  preferences: AccountPreferences | null;
  theme: AccountPreferences | null;
  setTheme: (theme: AccountPreferences | null) => void;
  setPreferences: (preferences: AccountPreferences | null) => void;
  applyTheme: (prefs: Partial<AccountPreferences>) => void;
  hydratePreferences: (prefs: AccountPreferences) => void;
  reloadPreferences: () => Promise<AccountPreferences | null>;
  savePreferences: (prefs: AccountPreferences) => Promise<AccountPreferences>;
  isLoading: boolean;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);
const PREFERENCES_CACHE_KEY = 'axi_preferences_cache';

function getSystemPrefersDark() {
  if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
    return true;
  }

  return window.matchMedia('(prefers-color-scheme: dark)').matches;
}

function applyDocumentTheme(prefs: Partial<AccountPreferences>) {
  if (typeof document === 'undefined') {
    return;
  }

  const themeMode = prefs.theme_mode;
  if (themeMode) {
    const resolvedTheme =
      themeMode === 'system'
        ? getSystemPrefersDark()
          ? 'dark'
          : 'light'
        : themeMode;

    document.documentElement.setAttribute('data-theme-mode', themeMode);
    document.documentElement.setAttribute('data-theme', resolvedTheme);
    document.documentElement.style.setProperty('--theme-mode', resolvedTheme);
    document.documentElement.style.colorScheme = resolvedTheme;
    document.documentElement.classList.toggle('dark', resolvedTheme === 'dark');
    document.documentElement.classList.toggle('light', resolvedTheme === 'light');
    document.documentElement.classList.toggle('theme-dark', resolvedTheme === 'dark');
    document.documentElement.classList.toggle('theme-light', resolvedTheme === 'light');
  }

  if (prefs.accent_color) {
    const colorValue = getColorValue(prefs.accent_color);
    document.documentElement.style.setProperty('--accent-color', colorValue);
    document.documentElement.style.setProperty('--accent-rgb', getColorRgbTriplet(prefs.accent_color));
    document.documentElement.setAttribute('data-accent', prefs.accent_color);
  }

  if (prefs.language) {
    document.documentElement.lang = prefs.language;
  }
}

function readCachedPreferences(): Partial<AccountPreferences> | null {
  const cached = localStorage.getItem(PREFERENCES_CACHE_KEY) ?? localStorage.getItem('axi_theme_cache');
  if (!cached) {
    return null;
  }

  try {
    return JSON.parse(cached) as Partial<AccountPreferences>;
  } catch (err) {
    console.error('Failed to parse cached preferences:', err);
    return null;
  }
}

function writeCachedPreferences(prefs: Partial<AccountPreferences>) {
  const cachePayload = {
    theme_mode: prefs.theme_mode,
    accent_color: prefs.accent_color,
    language: prefs.language,
  };

  localStorage.setItem(PREFERENCES_CACHE_KEY, JSON.stringify(cachePayload));
  localStorage.setItem('axi_theme_cache', JSON.stringify(cachePayload));
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}

interface ThemeProviderProps {
  children: React.ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [theme, setTheme] = useState<AccountPreferences | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const applyTheme = useCallback((prefs: Partial<AccountPreferences>) => {
    if (!prefs.theme_mode && !prefs.accent_color && !prefs.language) {
      return;
    }

    applyDocumentTheme(prefs);
    writeCachedPreferences(prefs);
  }, []);

  const hydratePreferences = useCallback(
    (prefs: AccountPreferences) => {
      setTheme(prefs);
      applyTheme(prefs);
    },
    [applyTheme],
  );

  const reloadPreferences = useCallback(async () => {
    const prefs = await getAccountPreferences();
    hydratePreferences(prefs);
    return prefs;
  }, [hydratePreferences]);

  const savePreferences = useCallback(
    async (prefs: AccountPreferences) => {
      const updated = await updateAccountPreferences(prefs);
      hydratePreferences(updated);
      return updated;
    },
    [hydratePreferences],
  );

  useEffect(() => {
    const cached = readCachedPreferences();
    if (cached) {
      applyTheme(cached);
    }
    setIsLoading(false);
  }, [applyTheme]);

  useEffect(() => {
    if (typeof window === 'undefined' || typeof window.matchMedia !== 'function') {
      return;
    }

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    const handleSystemThemeChange = () => {
      const cached = theme ?? readCachedPreferences();
      if (cached?.theme_mode === 'system') {
        applyTheme(cached);
      }
    };

    handleSystemThemeChange();
    mediaQuery.addEventListener('change', handleSystemThemeChange);
    return () => mediaQuery.removeEventListener('change', handleSystemThemeChange);
  }, [applyTheme, theme]);

  const value = useMemo(
    () => ({
      preferences: theme,
      theme,
      setTheme,
      setPreferences: setTheme,
      applyTheme,
      hydratePreferences,
      reloadPreferences,
      savePreferences,
      isLoading,
    }),
    [applyTheme, hydratePreferences, isLoading, reloadPreferences, savePreferences, theme],
  );

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}
