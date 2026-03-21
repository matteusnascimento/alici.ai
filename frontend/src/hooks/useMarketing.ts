import { useState } from 'react';

import { generateCampaign } from '../services/marketing.service';
import type { MarketingCampaignInput, MarketingCampaignResult } from '../types/marketing';

export function useMarketing() {
  const [result, setResult] = useState<MarketingCampaignResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runCampaign(payload: MarketingCampaignInput) {
    setLoading(true);
    try {
      const generated = await generateCampaign(payload);
      setResult(generated);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Falha ao gerar campanha');
      throw err;
    } finally {
      setLoading(false);
    }
  }

  return { result, loading, error, runCampaign };
}
