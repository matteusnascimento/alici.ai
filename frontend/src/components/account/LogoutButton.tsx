interface LogoutButtonProps {
  onLogout: () => void;
}

export function LogoutButton({ onLogout }: LogoutButtonProps) {
  return (
    <button
      type="button"
      onClick={onLogout}
      className="rounded-2xl border border-white/20 px-4 py-2 text-sm text-slate-100 transition hover:border-coral hover:text-coral"
    >
      Sign out
    </button>
  );
}
