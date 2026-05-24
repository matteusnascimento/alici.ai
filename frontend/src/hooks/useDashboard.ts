import { useEffect, useState } from 'react';

import { getDashboardStats } from '../services/dashboard.service';
import type { DashboardStats } from '../types/dashboard';

export function useDashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadStats() {
    setLoading(true);
    try {
      const result = await getDashboardStats();
      setStats({
        ...result,
        usage_bars: Array.isArray(result?.usage_bars) ? result.usage_bars : [],
      });
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao carregar dashboard');
      setStats(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadStats();
  }, []);

  return { stats, loading, error, reload: loadStats };
}
