import { SimpleWorkspacePage } from './SimpleWorkspacePage';

export function RemoveBackgroundStudioPage() {
  return (
    <SimpleWorkspacePage
      type="remove-background"
      title="Remover Fundo"
      subtitle="Fluxo visual de recorte com mascara IA, refinamento e troca de background"
      tools={['Mascara IA', 'Refine Edge', 'Softness', 'Invert']}
      promptPlaceholder="Descreva o recorte desejado"
    />
  );
}
