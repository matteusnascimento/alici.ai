import { useEffect, useState } from 'react';

import { getHelpInfo } from '../../../services/account.service';
import type { AccountHelpInfo } from '../../../types/account';

export function AccountHelpPage() {
  const [info, setInfo] = useState<AccountHelpInfo | null>(null);

  useEffect(() => {
    void getHelpInfo().then(setInfo);
  }, []);

  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
      <h2 className="font-display text-2xl text-white">Help / About</h2>
      {!info ? (
        <p className="mt-3 text-sm text-slate-300">Carregando informacoes...</p>
      ) : (
        <div className="mt-4 space-y-3 text-sm text-slate-100">
          <p>Versao do app: {info.app_version}</p>
          <a className="text-cyan underline" href={info.help_center_url} target="_blank" rel="noreferrer">
            Help center
          </a>
          <a className="block text-cyan underline" href={info.report_bug_url} target="_blank" rel="noreferrer">
            Report bug
          </a>
        </div>
      )}
    </section>
  );
}
