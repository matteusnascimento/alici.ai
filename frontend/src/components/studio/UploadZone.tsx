interface UploadZoneProps {
  label: string;
  onSelect: (files: FileList | null) => void;
}

export function UploadZone({ label, onSelect }: UploadZoneProps) {
  return (
    <label className="flex min-h-[130px] cursor-pointer items-center justify-center rounded-2xl border border-dashed border-white/20 bg-ink/40 px-4 text-center text-sm text-slate-300">
      <input type="file" multiple className="hidden" onChange={(event) => onSelect(event.target.files)} />
      {label}
    </label>
  );
}
