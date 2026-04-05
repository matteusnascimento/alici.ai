import { SimpleWorkspacePage } from './SimpleWorkspacePage';

export function BannerStudioPage() {
  return (
    <SimpleWorkspacePage
      type="banner"
      title="Banner com IA"
      subtitle="Componha banners para campanhas com variacoes por canal"
      tools={['Layout', 'Texto', 'Imagens', 'CTA', 'Branding']}
      promptPlaceholder="Crie um banner para campanha de performance"
    />
  );
}
