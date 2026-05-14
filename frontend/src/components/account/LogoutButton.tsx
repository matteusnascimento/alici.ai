interface LogoutButtonProps {
  onLogout: () => void;
}

export function LogoutButton({ onLogout }: LogoutButtonProps) {
  return (
    <button
      type="button"
      onClick={onLogout}
      className="rounded-2xl border border-coral/40 bg-coral/10 px-4 py-2 text-sm font-semibold text-coral transition hover:border-coral hover:bg-coral/15"
    >
      Sign out
    </button>
  );
}
