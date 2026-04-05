import type { AccountProfile } from '../../types/account';

interface ProfileCardProps {
  profile: AccountProfile;
  onEdit: () => void;
}

export function ProfileCard({ profile, onEdit }: ProfileCardProps) {
  const initials = profile.name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();

  return (
    <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-4">
          {profile.avatar_url ? (
            <img src={profile.avatar_url} alt={profile.name} className="h-16 w-16 rounded-2xl object-cover" />
          ) : (
            <div className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-cyan/15 font-display text-xl text-cyan">{initials}</div>
          )}
          <div>
            <p className="font-display text-2xl text-white">{profile.name}</p>
            <p className="text-sm text-slate-300">@{profile.username}</p>
            <p className="text-sm text-slate-300">{profile.email}</p>
          </div>
        </div>
        <div className="text-right">
          <span className="inline-flex rounded-full border border-cyan/30 bg-cyan/10 px-3 py-1 text-xs uppercase tracking-[0.2em] text-cyan">Plano {profile.plan}</span>
          <button type="button" onClick={onEdit} className="mt-3 block rounded-2xl border border-white/20 px-4 py-2 text-sm text-slate-100">
            Editar perfil
          </button>
        </div>
      </div>
      {profile.phone ? <p className="mt-3 text-sm text-slate-300">Telefone: {profile.phone}</p> : null}
      {profile.bio ? <p className="mt-2 text-sm text-slate-300">Bio: {profile.bio}</p> : null}
    </section>
  );
}
