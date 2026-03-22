import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';

vi.mock('../hooks/useMarketing', () => ({
  useMarketing: () => ({
    result: null,
    loading: false,
    error: null,
    runCampaign: vi.fn(async () => undefined),
  }),
}));

import { MarketingPanel } from '../components/platform/MarketingPanel';

describe('MarketingPanel', () => {
  it('renderiza formulario de geracao', () => {
    render(<MarketingPanel />);
    expect(screen.getByText(/Gerar campanha textual/i)).toBeInTheDocument();
  });
});
