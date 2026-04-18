import { useEffect } from 'react';

import { useTheme } from '../contexts/ThemeContext';

/**
 * Hook para carregar e aplicar as preferências de tema do usuário
 * ao inicializar a aplicação (deve ser chamado quando o usuário está autenticado)
 */
export function useInitializeTheme(enabled = true) {
  const { reloadPreferences } = useTheme();

  useEffect(() => {
    if (!enabled) {
      return;
    }

    const initializeUserTheme = async () => {
      try {
        await reloadPreferences();
      } catch (error) {
        console.warn('Failed to load user preferences:', error);
      }
    };

    void initializeUserTheme();
  }, [enabled, reloadPreferences]);
}
