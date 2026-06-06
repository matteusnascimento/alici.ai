import { ShieldCheck } from 'lucide-react';
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
      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
        <div className="flex items-center gap-3">
          <ShieldCheck size={20} className="text-emerald-400" />
          <h2 className="font-display text-2xl text-white">Seguranca da Conta</h2>
        </div>

        {summary ? (
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Sessoes ativas</p>
              <p className="mt-1 text-2xl font-semibold text-white">{summary.session_count}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Alertas</p>
              <p className={`mt-1 text-sm font-semibold ${summary.security_alerts ? 'text-amber-300' : 'text-emerald-300'}`}>
                {summary.security_alerts ? 'Atencao necessaria' : 'Tudo OK'}
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Ultima troca de senha</p>
              <p className="mt-1 text-sm text-slate-200">
                {summary.password_last_changed
                  ? new Date(summary.password_last_changed).toLocaleDateString('pt-BR')
                  : 'Nao informada'}
              </p>
            </div>
          </div>
        ) : (
          <p className="mt-3 text-sm text-slate-400">Carregando resumo...</p>
        )}
      </section>

      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-semibold text-white">Sessoes Ativas</h3>
          <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">
            {summary?.session_count ?? 0} ativa{summary?.session_count === 1 ? '' : 's'}
          </span>
        </div>
        <div className="rounded-2xl border border-dashed border-white/10 bg-white/[0.02] p-5 text-sm leading-6 text-slate-400">
          A plataforma ainda nao possui lista detalhada de sessoes por dispositivo. O total acima vem do backend; acoes de encerramento
          remoto ficam indisponiveis ate o suporte de sessoes revogaveis estar ativo.
        </div>
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
