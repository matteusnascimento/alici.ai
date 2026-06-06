import { FileUp, Upload } from 'lucide-react';

export function StudioImportPage() {
  return (
    <main className="min-h-[calc(100vh-2rem)] rounded-[2rem] border border-white/10 bg-[radial-gradient(circle_at_14%_0%,rgba(192,38,211,0.18),transparent_34%),linear-gradient(180deg,#050507,#0a0a12)] p-6 text-white shadow-[var(--studio-shadow)]">
      <p className="text-xs font-bold uppercase tracking-[0.28em] text-cyan-300">Importacao</p>
      <h1 className="mt-3 font-display text-3xl font-black">Importar arquivo para o Studio</h1>
      <p className="mt-2 max-w-2xl text-sm text-slate-300">
        Designs exportados de outras ferramentas entram aqui como PNG, PDF, JPG ou MP4. Nao ha integracao direta com Canva; o arquivo vira um asset do AXI Studio.
      </p>
      <label className="mt-8 flex min-h-72 cursor-pointer flex-col items-center justify-center rounded-3xl border border-dashed border-cyan-300/35 bg-cyan-300/8 p-8 text-center">
        <Upload className="h-10 w-10 text-cyan-200" />
        <span className="mt-4 text-lg font-bold">Enviar PNG, PDF, JPG ou MP4</span>
        <span className="mt-2 text-sm text-slate-300">MVP: upload visual preparado; persistencia de assets remotos permanece no backend existente.</span>
        <input type="file" accept="image/png,image/jpeg,application/pdf,video/mp4" className="hidden" />
      </label>
      <div className="mt-5 flex items-center gap-3 rounded-2xl border border-white/10 bg-white/[0.055] p-4 text-sm text-slate-300">
        <FileUp size={18} className="text-cyan-200" />
        Importacao futura preserva o arquivo como asset. Edicao por layers depende de conversao propria do AXI, nao de API externa.
      </div>
    </main>
  );
}
