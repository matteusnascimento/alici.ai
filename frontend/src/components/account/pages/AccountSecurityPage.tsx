import { useEffect, useState } from 'react';

import { changePassword, getSecuritySummary } from '../../../services/security.service';
import type { AccountSecuritySummary } from '../../../types/account';
import { SecurityForm } from '../SecurityForm';

export function AccountSecurityPage() {
  const [summary, setSummary] = useState<AccountSecuritySummary | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    void getSecuritySummary().then(setSummary);
  }, []);

  return (
    <div className="space-y-4">
      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
        <h2 className="font-display text-2xl text-white">Security Summary</h2>
        {summary ? (
          <div className="mt-3 space-y-1 text-sm text-slate-200">
            <p>Sessoes ativas: {summary.session_count}</p>
            <p>Alertas de seguranca: {summary.security_alerts ? 'ativos' : 'inativos'}</p>
            <p>
              Ultima alteracao de senha:{' '}
              {summary.password_last_changed ? new Date(summary.password_last_changed).toLocaleString('pt-BR') : 'nao informada'}
            </p>
          </div>
        ) : (
          <p className="mt-2 text-sm text-slate-300">Carregando resumo...</p>
        )}
      </section>
      <SecurityForm
        loading={saving}
        onSubmit={async (payload) => {
          setSaving(true);
          try {
            await changePassword(payload);
          } finally {
            setSaving(false);
          }
        }}
      />
    </div>
  );
}
