import { useParams } from 'react-router-dom';
import { useState } from 'react';

import { useAgentKnowledge } from '../../../hooks/agentsV2/useAgentKnowledge';
import { AgentFaqManager } from './AgentFaqManager';
import { AgentKnowledgeLibrary } from './AgentKnowledgeLibrary';
import { AgentKnowledgeUpload } from './AgentKnowledgeUpload';
import { AgentManualKnowledgeForm } from './AgentManualKnowledgeForm';

export function AgentKnowledgePage() {
  const params = useParams();
  const agentId = Number(params.id || 0);
  const { data, loading, error, saving, addFaq, addFile, addManual, remove } = useAgentKnowledge(agentId);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  if (loading) return <p className="text-slate-300">Carregando materiais...</p>;
  if (error) return <p className="text-red-300">{error}</p>;

  async function handleUploadFiles(files: File[]) {
    try {
      for (const file of files) {
        await addFile(file);
      }
      setFeedback(`${files.length} material(is) enviado(s) com sucesso.`);
    } catch (uploadError) {
      setFeedback(uploadError instanceof Error ? uploadError.message : 'Falha ao enviar materiais.');
    }
  }

  async function handleDelete(sourceId: number) {
    setDeletingId(sourceId);
    try {
      await remove(sourceId);
      setFeedback('Material removido com sucesso.');
    } catch (removeError) {
      setFeedback(removeError instanceof Error ? removeError.message : 'Falha ao remover material.');
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <div className="space-y-5">
      <header className="rounded-3xl border border-white/10 bg-gradient-to-r from-white/[0.08] to-white/[0.02] p-5">
        <p className="text-xs uppercase tracking-[0.2em] text-cyan-300">Central de treinamento</p>
        <h1 className="mt-1 font-display text-2xl text-white">Materiais e informacoes do agente</h1>
        <p className="mt-2 max-w-3xl text-sm text-slate-300">
          Estruture a base de conhecimento com arquivos, conteudos orientativos e FAQs para elevar a qualidade das respostas.
        </p>
      </header>

      {feedback ? (
        <div className="rounded-2xl border border-emerald-300/30 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-100">{feedback}</div>
      ) : null}

      <div className="grid gap-4 xl:grid-cols-2">
        <AgentKnowledgeUpload busy={saving} onUploadFiles={handleUploadFiles} />
        <AgentManualKnowledgeForm
          busy={saving}
          onSave={async (payload) => {
            try {
              await addManual(payload);
              setFeedback('Conteudo manual salvo com sucesso.');
            } catch (manualError) {
              setFeedback(manualError instanceof Error ? manualError.message : 'Falha ao salvar conteudo manual.');
            }
          }}
        />
      </div>

      <AgentFaqManager
        busy={saving}
        onAddFaq={async (question, answer) => {
          try {
            await addFaq({ question, answer });
            setFeedback('FAQ adicionada com sucesso.');
          } catch (faqError) {
            setFeedback(faqError instanceof Error ? faqError.message : 'Falha ao salvar FAQ.');
          }
        }}
      />

      <AgentKnowledgeLibrary items={data} deletingId={deletingId} onDelete={handleDelete} />
    </div>
  );
}
