import { useEffect, useState } from 'react';

import { getAccountIntegrations, setIntegrationStatus } from '../../../services/integrations.service';
import type { AccountIntegration } from '../../../types/account';
import { IntegrationCard } from '../IntegrationCard';

export function AccountAppsPage() {
  const [integrations, setIntegrations] = useState<AccountIntegration[]>([]);

  useEffect(() => {
    void getAccountIntegrations().then((data) => setIntegrations(Array.isArray(data) ? data : []));
  }, []);

  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
      <h2 className="font-display text-2xl text-white">Applications / Integrations</h2>
      <p className="mt-2 text-sm text-slate-300">Conecte e desconecte provedores como OpenAI, WhatsApp, Instagram e website widgets.</p>
      <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {integrations.map((integration) => (
          <IntegrationCard
            key={integration.id}
            integration={integration}
            onToggle={async (enabled) => {
              const updated = await setIntegrationStatus(integration.provider, enabled);
              setIntegrations((current) => current.map((item) => (item.id === updated.id ? updated : item)));
            }}
          />
        ))}
      </div>
    </section>
  );
}
