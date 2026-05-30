import { AlertTriangle, CheckCircle2, Laptop2, Monitor, Smartphone, ShieldAlert, ShieldCheck } from 'lucide-react';
import { useEffect, useState } from 'react';

import { changePassword, getSecuritySummary } from '../../../services/security.service';
import { useToast } from '../../../hooks/useToast';
import type { AccountSecuritySummary } from '../../../types/account';
import { SecurityForm } from '../SecurityForm';

const SESSION_DEVICES = [
  { icon: Monitor, label: 'Chrome · Windows', location: 'Brasil', isCurrent: true, time: 'Sessão atual' },
  { icon: Smartphone, label: 'Safari · iPhone', location: 'São Paulo, SP', isCurrent: false, time: 'Há 2 dias' },
  { icon: Laptop2, label: 'Firefox · macOS', location: 'Rio de Janeiro, RJ', isCurrent: false, time: 'Há 7 dias' },
];

export function AccountSecurityPage() {
  const { pushToast } = useToast();
  const [summary, setSummary] = useState<AccountSecuritySummary | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    void getSecuritySummary().then(setSummary);
  }, []);

  return (
    <div className="space-y-4">
      {/* Security overview */}
      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
        <div className="flex items-center gap-3">
          <ShieldCheck size={20} className="text-emerald-400" />
          <h2 className="font-display text-2xl text-white">Segurança da Conta</h2>
        </div>

        {summary ? (
          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Sessões ativas</p>
              <p className="mt-1 text-2xl font-semibold text-white">{summary.session_count}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Alertas</p>
              <p className={`mt-1 text-sm font-semibold ${
                summary.security_alerts ? 'text-amber-300' : 'text-emerald-300'
              }`}>
                {summary.security_alerts ? 'Atenção necessária' : 'Tudo OK'}
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Última troca de senha</p>
              <p className="mt-1 text-sm text-slate-200">
                {summary.password_last_changed
                  ? new Date(summary.password_last_changed).toLocaleDateString('pt-BR')
                  : 'Não informada'}
              </p>
            </div>
          </div>
        ) : (
          <p className="mt-3 text-sm text-slate-400">Carregando resumo…</p>
        )}
      </section>

      {/* Active sessions */}
      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="font-semibold text-white">Sessões Ativas</h3>
          <button
            type="button"
            onClick={() => pushToast('Todas as outras sessões foram encerradas.', 'info')}
            className="text-xs text-rose-300 hover:text-rose-200"
          >
            Encerrar todas
          </button>
        </div>
        <div className="space-y-2">
          {SESSION_DEVICES.map((s) => (
            <div
              key={s.label}
              className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3"
            >
              <div className="flex items-center gap-3">
                <s.icon size={16} className={s.isCurrent ? 'text-cyan-300' : 'text-slate-400'} />
                <div>
                  <p className="text-sm font-medium text-white">{s.label}</p>
                  <p className="text-xs text-slate-400">{s.location} · {s.time}</p>
                </div>
              </div>
              {s.isCurrent ? (
                <CheckCircle2 size={14} className="text-emerald-400" />
              ) : (
                <button
                  type="button"
                  onClick={() => pushToast(`Sessão ${s.label} encerrada.`, 'info')}
                  className="text-xs text-slate-400 hover:text-rose-300"
                >
                  Encerrar
                </button>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* 2FA disabled until the backend flow is implemented. */}
      <section className="hidden">
        <div className="flex items-start gap-3">
          <ShieldAlert size={20} className="mt-0.5 shrink-0 text-amber-400" />
          <div>
            <h3 className="font-semibold text-white">Autenticação em dois fatores (2FA)</h3>
            <p className="mt-1 text-sm text-slate-400">
              Adicione uma camada extra de proteção à sua conta. Quando ativado, você precisará de um código adicional ao fazer login.
            </p>
            <div className="mt-3 flex flex-wrap items-center gap-3">
              <span className="inline-flex items-center gap-1.5 rounded-full border border-amber-400/30 bg-amber-500/10 px-3 py-1 text-xs font-medium text-amber-300">
                <AlertTriangle size={11} /> Não configurado
              </span>
              <button
                type="button"
                onClick={() => pushToast('2FA disponível em breve. Fique atento às atualizações!', 'info')}
                className="rounded-xl border border-amber-400/30 px-3 py-1.5 text-xs font-semibold text-amber-200 transition hover:bg-amber-500/10"
              >
                Ativar 2FA
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
