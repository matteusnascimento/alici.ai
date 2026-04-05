import { SimpleWorkspacePage } from './SimpleWorkspacePage';

export function StoryStudioPage() {
  return (
    <SimpleWorkspacePage
      type="story"
      title="Story com IA"
      subtitle="Crie stories verticais prontos para anuncio, organic e sequencia de campanha"
      tools={['Templates', 'Stickers', 'Texto', 'Assets', 'Branding']}
      promptPlaceholder="Descreva o story que voce quer criar"
    />
  );
}
