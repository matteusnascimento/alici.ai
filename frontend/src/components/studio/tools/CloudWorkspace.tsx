import { useNavigate } from 'react-router-dom';

import { getCloudAssets } from '../../../services/studioService';
import { EmptyState } from '../EmptyState';

export function CloudWorkspace() {
  const navigate = useNavigate();
  const assets = getCloudAssets();

  return (
    <div className="space-y-4">
      <button type="button" onClick={() => navigate('/app/studio')} className="text-sm text-cyan">← Voltar para AXI Studio</button>
      <section className="rounded-3xl border border-white/10 bg-white/[0.03] p-5">
        <h2 className="font-display text-2xl text-white">Espaco / Cloud</h2>
        <p className="mt-2 text-sm text-slate-300">Ativos criativos e anexos de projeto, prontos para backend de storage.</p>

        {!assets.length ? (
          <EmptyState title="Sem ativos no cloud" description="Quando houver uploads vinculados a projetos, eles aparecem aqui." />
        ) : (
          <div className="mt-4 overflow-hidden rounded-2xl border border-white/10">
            <table className="w-full text-left text-sm">
              <thead className="bg-white/[0.03] text-slate-300">
                <tr>
                  <th className="px-4 py-3">Arquivo</th>
                  <th className="px-4 py-3">Categoria</th>
                  <th className="px-4 py-3">Tamanho</th>
                  <th className="px-4 py-3">Acao</th>
                </tr>
              </thead>
              <tbody>
                {assets.map((asset) => (
                  <tr key={asset.id} className="border-t border-white/10 text-slate-100">
                    <td className="px-4 py-3">{asset.name}</td>
                    <td className="px-4 py-3">{asset.category}</td>
                    <td className="px-4 py-3">{asset.sizeKb} KB</td>
                    <td className="px-4 py-3">
                      <button type="button" className="rounded-xl border border-white/20 px-3 py-1 text-xs">
                        Vincular projeto
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
