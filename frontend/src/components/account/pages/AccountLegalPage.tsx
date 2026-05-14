import { useEffect, useState } from 'react';

import { getLegalInfo } from '../../../services/account.service';
import type { AccountLegalInfo } from '../../../types/account';

export function AccountLegalPage() {
  const [info, setInfo] = useState<AccountLegalInfo | null>(null);

  useEffect(() => {
    void getLegalInfo().then(setInfo);
  }, []);

  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
      <h2 className="font-display text-2xl text-white">Legal</h2>
      {!info ? (
        <p className="mt-3 text-sm text-slate-300">Carregando informacoes legais...</p>
      ) : (
        <div className="mt-4 space-y-3 text-sm text-slate-100">
          <a className="text-cyan underline" href={info.terms_url} target="_blank" rel="noreferrer">
            Terms of use
          </a>
          <a className="block text-cyan underline" href={info.privacy_url} target="_blank" rel="noreferrer">
            Privacy policy
          </a>
        </div>
      )}
    </section>
  );
}
