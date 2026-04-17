import { FormEvent, useEffect, useState } from 'react';

import { useBilling } from '../../hooks/useBilling';
import { useSettings } from '../../hooks/useSettings';

export function AccountPanel() {
  const { account, loading, saving, error, saveProfile, saveSettings } = useSettings();
  const { plans, current, usage, upgrading, startCheckout, openPortal, cancel, resume, error: billingError } = useBilling();
  const [upgradeMessage, setUpgradeMessage] = useState<string | null>(null);
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');
  const [profile, setProfile] = useState({ name: '', username: '', email: '', phone: '' });
  const [settings, setLocalSettings] = useState({
    background_conversation: true,
    autocomplete: true,
    trending: true,
    sequence: false,
    split_mode: false,
    language: 'pt-BR',
    voice: 'neutral',
  });

  useEffect(() => {
    if (account) {
      setProfile({
        name: account.profile.name,
        username: account.profile.username,
        email: account.profile.email,
        phone: account.profile.phone || '',
      });
      setLocalSettings(account.settings);
    }
  }, [account]);

  async function handleProfileSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await saveProfile(profile);
  }

  async function handleSettingsSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await saveSettings(settings);
  }

  if (loading) {
    return <div className="panel-base">Carregando conta...</div>;
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
      <section className="panel-base">
        <h3 className="font-display text-2xl text-white">Perfil</h3>
        <form className="mt-6 grid gap-4" onSubmit={handleProfileSubmit}>
          {[
            ['name', 'Nome'],
            ['username', 'Username'],
            ['email', 'Email'],
            ['phone', 'Telefone'],
          ].map(([key, label]) => (
            <div key={key}>
              <label className="mb-2 block text-sm text-slate-300">{label}</label>
              <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none focus:border-cyan" type={key === 'email' ? 'email' : 'text'} value={profile[key as keyof typeof profile]} onChange={(event) => setProfile((current) => ({ ...current, [key]: event.target.value }))} required={key !== 'phone'} />
            </div>
          ))}
          <button className="rounded-2xl bg-sand px-4 py-3 font-semibold text-ink transition hover:bg-white disabled:opacity-60" disabled={saving} type="submit">
            Salvar perfil
          </button>
        </form>
      </section>
      <section className="panel-base">
        <h3 className="font-display text-2xl text-white">Configurações AXI</h3>
        <form className="mt-6 space-y-4" onSubmit={handleSettingsSubmit}>
          {[
            ['background_conversation', 'Background conversation'],
            ['autocomplete', 'Autocomplete'],
            ['trending', 'Trending'],
            ['sequence', 'Sequence'],
            ['split_mode', 'Split mode'],
          ].map(([key, label]) => (
            <label key={key} className="flex items-center justify-between rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white">
              <span>{label}</span>
              <input checked={settings[key as keyof typeof settings] as boolean} onChange={(event) => setLocalSettings((current) => ({ ...current, [key]: event.target.checked }))} type="checkbox" />
            </label>
          ))}
          {[
            ['language', 'Idioma'],
            ['voice', 'Voz'],
          ].map(([key, label]) => (
            <div key={key}>
              <label className="mb-2 block text-sm text-slate-300">{label}</label>
              <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none focus:border-cyan" value={settings[key as keyof typeof settings] as string} onChange={(event) => setLocalSettings((current) => ({ ...current, [key]: event.target.value }))} />
            </div>
          ))}
          <button className="rounded-2xl bg-sand px-4 py-3 font-semibold text-ink transition hover:bg-white disabled:opacity-60" disabled={saving} type="submit">
            Salvar configurações
          </button>
        </form>
        {error ? <p className="mt-4 text-sm text-coral">{error}</p> : null}
      </section>
      <section className="panel-base xl:col-span-2">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <h3 className="font-display text-2xl text-white">Assinatura</h3>
          <div className="flex flex-wrap items-center gap-2 text-sm text-slate-300">
            <p>
              Plano atual: <span className="font-semibold text-white">{current?.plan_name ?? account?.profile.plan ?? 'free'}</span>
            </p>
            {current?.next_renewal_at ? <p>• Renova em: {new Date(current.next_renewal_at).toLocaleDateString('pt-BR')}</p> : null}
            {current?.cancel_at_period_end ? <p className="text-amber-300">• Cancelamento ao fim do período</p> : null}
          </div>
        </div>

        <div className="mt-4 flex flex-wrap items-center gap-3">
          <div className="inline-flex rounded-xl border border-white/15 bg-black/20 p-1 text-xs">
            <button
              type="button"
              onClick={() => setBillingCycle('monthly')}
              className={`rounded-lg px-3 py-1.5 transition ${billingCycle === 'monthly' ? 'bg-cyan/20 text-cyan' : 'text-slate-300 hover:text-white'}`}
            >
              Mensal
            </button>
            <button
              type="button"
              onClick={() => setBillingCycle('yearly')}
              className={`rounded-lg px-3 py-1.5 transition ${billingCycle === 'yearly' ? 'bg-cyan/20 text-cyan' : 'text-slate-300 hover:text-white'}`}
            >
              Anual
            </button>
          </div>
          <button
            type="button"
            onClick={() => {
              void openPortal();
            }}
            className="rounded-2xl border border-white/20 px-4 py-2 text-xs font-semibold text-slate-100 transition hover:border-cyan/45 hover:text-cyan"
          >
            Gerenciar assinatura
          </button>
          {current?.cancel_at_period_end ? (
            <button
              type="button"
              onClick={async () => {
                try {
                  const message = await resume();
                  setUpgradeMessage(message);
                } catch {
                  setUpgradeMessage(null);
                }
              }}
              className="rounded-2xl border border-emerald-400/30 px-4 py-2 text-xs font-semibold text-emerald-300 transition hover:border-emerald-300/60"
            >
              Reativar assinatura
            </button>
          ) : (
            <button
              type="button"
              onClick={async () => {
                try {
                  const message = await cancel();
                  setUpgradeMessage(message);
                } catch {
                  setUpgradeMessage(null);
                }
              }}
              className="rounded-2xl border border-amber-400/30 px-4 py-2 text-xs font-semibold text-amber-300 transition hover:border-amber-300/60"
            >
              Cancelar no fim do período
            </button>
          )}
        </div>

        {usage ? (
          <div className="mt-5 grid gap-3 md:grid-cols-2">
            {usage.items.map((item) => (
              <article key={item.metric} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <p className="text-sm uppercase tracking-[0.2em] text-slate-300">{item.metric}</p>
                <p className="mt-2 text-white">
                  {item.used} / {item.limit}
                </p>
              </article>
            ))}
          </div>
        ) : null}

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          {plans.map((plan) => (
            <article key={plan.id} className="rounded-3xl border border-white/10 bg-white/5 p-5">
              <p className="text-sm uppercase tracking-[0.2em] text-cyan">{plan.name}</p>
              <p className="mt-3 font-display text-3xl text-white">
                R$ {(billingCycle === 'yearly' ? plan.yearly_price ?? plan.monthly_price : plan.monthly_price).toFixed(0)}
                <span className="text-sm text-slate-300">/{billingCycle === 'yearly' ? 'ano' : 'mes'}</span>
              </p>
              <ul className="mt-4 space-y-2 text-sm text-slate-200">
                {plan.features.slice(0, 3).map((feature) => (
                  <li key={feature}>- {feature}</li>
                ))}
              </ul>
              <button
                className="mt-5 w-full rounded-2xl bg-sand px-4 py-3 font-semibold text-ink transition hover:bg-white disabled:opacity-60"
                disabled={upgrading || current?.plan_id === plan.id}
                onClick={async () => {
                  try {
                    await startCheckout(plan.id, billingCycle);
                    const message = 'Redirecionando para checkout seguro...';
                    setUpgradeMessage(message);
                  } catch {
                    setUpgradeMessage(null);
                  }
                }}
                type="button"
              >
                {current?.plan_id === plan.id ? 'Plano ativo' : upgrading ? 'Atualizando...' : 'Fazer upgrade'}
              </button>
            </article>
          ))}
        </div>
        {upgradeMessage ? <p className="mt-4 text-sm text-cyan">{upgradeMessage}</p> : null}
        {billingError ? <p className="mt-2 text-sm text-rose-200">{billingError}</p> : null}
      </section>
    </div>
  );
}
