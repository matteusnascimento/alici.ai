import { AlertTriangle, ShieldAlert, ShieldCheck } from 'lucide-react';
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
          <button type="button" disabled className="cursor-not-allowed text-xs text-slate-500">
            Encerrar todas
          </button>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
          <p className="text-sm font-medium text-white">
            {summary ? `${summary.session_count} sessao(oes) ativa(s) informada(s) pelo backend` : 'Carregando sessoes...'}
          </p>
          <p className="mt-1 text-xs text-slate-400">
            O detalhamento por dispositivo nao esta disponivel na API atual; nenhum dispositivo ficticio sera exibido.
          </p>
        </div>
      </section>

      <section className="rounded-3xl border border-amber-400/20 bg-amber-500/5 p-6">
        <div className="flex items-start gap-3">
          <ShieldAlert size={20} className="mt-0.5 shrink-0 text-amber-400" />
          <div>
            <h3 className="font-semibold text-white">Autenticacao em dois fatores (2FA)</h3>
            <p className="mt-1 text-sm text-slate-400">
              A API atual ainda nao fornece ativacao de 2FA. A tela mantem a acao bloqueada ate existir suporte real.
            </p>
            <div className="mt-3 flex flex-wrap items-center gap-3">
              <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-400/30 bg-amber-500/10 px-3 py-1 text-xs font-medium text-amber-300">
                <AlertTriangle size={11} /> Nao configurado
              </span>
              <button
                type="button"
                disabled
                className="cursor-not-allowed rounded-xl border border-amber-400/20 px-3 py-1.5 text-xs font-semibold text-amber-300/70"
              >
                Indisponivel
              </button>
            </div>
          </div>
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
