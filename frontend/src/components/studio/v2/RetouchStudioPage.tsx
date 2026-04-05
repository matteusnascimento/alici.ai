import { SimpleWorkspacePage } from './SimpleWorkspacePage';

export function RetouchStudioPage() {
  return (
    <SimpleWorkspacePage
      type="retouch"
      title="Retoque IA"
      subtitle="Retoque fino para anuncios, produtos e criativos de alta conversao"
      tools={['Pele', 'Detalhe', 'Luz', 'Cor', 'Sharpen']}
      promptPlaceholder="Descreva o retoque que voce quer aplicar"
    />
  );
}
