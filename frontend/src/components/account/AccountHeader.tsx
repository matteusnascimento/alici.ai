import type { AccountProfile } from '../../types/account';
import type { CurrentSubscription } from '../../types/billing';
import { buildInitialsSafe } from '../../utils/dataHelpers';

interface AccountHeaderProps {
  title: string;
  subtitle: string;
  profile?: AccountProfile | null;
  subscription?: CurrentSubscription | null;
}

export function AccountHeader({ title, subtitle, profile, subscription }: AccountHeaderProps) {
  const initials = buildInitialsSafe(profile?.name);

  return (
    <header className="relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-[#0b1a2b] via-[#0d1f34] to-[#091524] p-5 md:p-7">
      <div className="pointer-events-none absolute -right-16 -top-16 h-44 w-44 rounded-full bg-cyan/15 blur-3xl" />
      <div className="pointer-events-none absolute bottom-0 left-0 h-px w-full bg-gradient-to-r from-transparent via-white/30 to-transparent" />

      <div className="relative flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
        <div className="max-w-2xl">
          <p className="text-[11px] uppercase tracking-[0.32em] text-cyan/90">AXI Account Center</p>
          <h1 className="mt-3 font-display text-3xl text-white md:text-4xl">{title}</h1>
          <p className="mt-2 text-sm text-slate-300 md:text-base">{subtitle}</p>
        </div>

        <section className="min-w-[280px] rounded-2xl border border-white/15 bg-white/[0.04] p-4 backdrop-blur-sm">
          <div className="flex items-center gap-3">
            {profile?.avatar_url ? (
              <img src={profile.avatar_url} alt={profile.name} className="h-11 w-11 rounded-xl object-cover" />
            ) : (
              <div className="inline-flex h-11 w-11 items-center justify-center rounded-xl bg-cyan/15 font-display text-sm text-cyan">{initials}</div>
            )}
            <div>
              <p className="text-sm font-semibold text-white">{profile?.name ?? 'Sua conta AXI'}</p>
              <p className="text-xs text-slate-300">{profile?.email ?? 'Conta autenticada'}</p>
            </div>
          </div>
          <div className="mt-3 flex items-center justify-between rounded-xl border border-white/10 bg-black/20 px-3 py-2">
            <div>
              <p className="text-[10px] uppercase tracking-[0.24em] text-slate-400">Plano atual</p>
              <p className="text-sm font-semibold text-white">{subscription?.plan_name ?? profile?.plan ?? 'Free'}</p>
            </div>
            <span className="rounded-full border border-cyan/40 bg-cyan/10 px-2.5 py-1 text-[10px] uppercase tracking-[0.2em] text-cyan">
              {subscription?.status ?? 'active'}
            </span>
          </div>
        </section>
      </div>
    </header>
  );
}
