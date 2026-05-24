interface AvatarUploaderProps {
  value: string;
  onChange: (next: string) => void;
}

export function AvatarUploader({ value, onChange }: AvatarUploaderProps) {
  return (
    <label className="block space-y-2 text-sm text-slate-300">
      <span>Avatar URL</span>
      <input
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="w-full rounded-2xl border border-white/10 bg-ink/60 px-4 py-3 text-white outline-none focus:border-cyan"
        placeholder="https://..."
      />
    </label>
  );
}
