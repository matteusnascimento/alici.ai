import type React from 'react';
import { useEffect, useState } from 'react';

declare global {
  namespace JSX {
    interface IntrinsicElements {
      'stripe-pricing-table': React.DetailedHTMLProps<React.HTMLAttributes<HTMLElement>, HTMLElement> & {
        'pricing-table-id': string;
        'publishable-key': string;
      };
    }
  }
}

const STRIPE_SCRIPT_ID = 'stripe-pricing-table-script';
const STRIPE_SCRIPT_SRC = 'https://js.stripe.com/v3/pricing-table.js';
const FALLBACK_PRICING_TABLE_ID = 'prctbl_1TMziC1R77fHca3odwEWCg1X';
const FALLBACK_PUBLISHABLE_KEY = 'pk_test_51TMHSV1R77fHca3o3W6gnqYbhKD5cpmJlrpknuHvEb8YSVi8MUKBppoGjEEZ0e9kvqVnDwd0gS9kqUxAPsdW7CNG0057XWIrwI';

function resolveConfig() {
  const pricingTableId = import.meta.env.VITE_STRIPE_PRICING_TABLE_ID || FALLBACK_PRICING_TABLE_ID;
  const publishableKey = import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || FALLBACK_PUBLISHABLE_KEY;
  return { pricingTableId, publishableKey };
}

export function StripePricingTable() {
  const [{ loaded, failed }, setStatus] = useState({ loaded: false, failed: false });
  const { pricingTableId, publishableKey } = resolveConfig();

  useEffect(() => {
    let mounted = true;

    const applyLoaded = () => {
      if (mounted) {
        setStatus({ loaded: true, failed: false });
      }
    };

    const applyFailed = () => {
      if (mounted) {
        setStatus({ loaded: false, failed: true });
      }
    };

    const existing = document.getElementById(STRIPE_SCRIPT_ID) as HTMLScriptElement | null;
    if (existing) {
      if (existing.dataset.loaded === 'true') {
        applyLoaded();
      } else {
        existing.addEventListener('load', applyLoaded);
        existing.addEventListener('error', applyFailed);
      }
      return () => {
        mounted = false;
        existing.removeEventListener('load', applyLoaded);
        existing.removeEventListener('error', applyFailed);
      };
    }

    const script = document.createElement('script');
    script.id = STRIPE_SCRIPT_ID;
    script.src = STRIPE_SCRIPT_SRC;
    script.async = true;
    script.onload = () => {
      script.dataset.loaded = 'true';
      applyLoaded();
    };
    script.onerror = () => {
      script.dataset.loaded = 'false';
      applyFailed();
    };

    document.body.appendChild(script);

    return () => {
      mounted = false;
      script.onload = null;
      script.onerror = null;
    };
  }, []);

  if (!pricingTableId || !publishableKey) {
    return <p className="rounded-2xl border border-rose-400/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">Nao foi possivel carregar os planos no momento.</p>;
  }

  if (failed) {
    return <p className="rounded-2xl border border-rose-400/40 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">Nao foi possivel carregar os planos no momento.</p>;
  }

  if (!loaded) {
    return <p className="rounded-2xl border border-white/10 bg-black/20 px-4 py-3 text-sm text-slate-200">Carregando planos...</p>;
  }

  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-2">
      <stripe-pricing-table pricing-table-id={pricingTableId} publishable-key={publishableKey} />
    </div>
  );
}
