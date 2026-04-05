import { SimpleWorkspacePage } from './SimpleWorkspacePage';

export function CaptionsStudioPage() {
  return (
    <SimpleWorkspacePage
      type="captions"
      title="Legendas e Copy"
      subtitle="Legendas automaticas, CTA generator, headlines e roteiro em fluxo criativo"
      tools={['Legendas', 'Copy', 'CTA', 'Headline', 'Descricao', 'Roteiro']}
      promptPlaceholder="Escreva o contexto para gerar legenda e copy"
    />
  );
}
