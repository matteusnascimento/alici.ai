import type { AccountProfile } from '../../types/account';
import { buildInitialsSafe } from '../../utils/dataHelpers';

interface ProfileCardProps {
  profile: AccountProfile;
  onEdit: () => void;
}

export function ProfileCard({ profile, onEdit }: ProfileCardProps) {
  const initials = buildInitialsSafe(profile?.name);

  return (
    <section className="overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-[#0c1c2e] via-[#0d1a2b] to-[#091322] p-5 md:p-6">
      <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex items-center gap-4 md:gap-5">
          {profile.avatar_url ? (
            <img src={profile.avatar_url} alt={profile.name} className="h-16 w-16 rounded-2xl object-cover md:h-20 md:w-20" />
          ) : (
            <div className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-cyan/15 font-display text-xl text-cyan md:h-20 md:w-20 md:text-2xl">
              {initials}
            </div>
          )}
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-slate-400">Perfil principal</p>
            <p className="mt-1 font-display text-2xl text-white md:text-3xl">{profile.name}</p>
            <p className="text-sm text-slate-300">@{profile.username}</p>
            <p className="text-sm text-slate-300">{profile.email}</p>
          </div>
        </div>
        <div className="flex flex-col items-start gap-3 lg:items-end">
          <span className="inline-flex rounded-full border border-cyan/30 bg-cyan/10 px-3 py-1 text-xs uppercase tracking-[0.2em] text-cyan">Plano {profile.plan}</span>
          <button
            type="button"
            onClick={onEdit}
            className="rounded-2xl border border-white/25 bg-white/[0.04] px-4 py-2 text-sm font-semibold text-slate-100 transition hover:border-cyan/45 hover:text-cyan"
          >
            Editar perfil
          </button>
        </div>
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-3">
          <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Email</p>
          <p className="mt-2 text-sm text-slate-100">{profile.email}</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-3">
          <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Telefone</p>
          <p className="mt-2 text-sm text-slate-100">{profile.phone ?? 'Nao informado'}</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-3">
          <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Usuario</p>
          <p className="mt-2 text-sm text-slate-100">@{profile.username}</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-3">
          <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">Plano</p>
          <p className="mt-2 text-sm text-slate-100">{profile.plan}</p>
        </div>
      </div>

      {profile.bio ? <p className="mt-4 text-sm leading-relaxed text-slate-300">{profile.bio}</p> : null}
    </section>
  );
}
