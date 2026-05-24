import { getColorValue } from '../../utils/colorMap';

interface ThemePreviewProps {
  accentColor: string;
  themeMode: string;
}

export function ThemePreview({ accentColor, themeMode }: ThemePreviewProps) {
  const colorValue = getColorValue(accentColor);
  const isDark = themeMode === 'dark';

  return (
    <div
      style={{
        backgroundColor: isDark ? '#08111f' : '#ffffff',
        color: isDark ? '#ffffff' : '#08111f',
      }}
      className="rounded-2xl border border-white/10 p-6 transition-all duration-300"
    >
      <p className="text-sm font-medium text-slate-400 mb-4">Prévia do tema</p>
      
      <div className="space-y-4">
        {/* Card exemplo */}
        <div
          style={{
            backgroundColor: isDark ? '#0F172A' : '#f8fafc',
            borderColor: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
            color: isDark ? '#ffffff' : '#000000',
          }}
          className="rounded-xl border p-4"
        >
          <p className="text-xs text-slate-400 mb-2">Exemplo de card</p>
          <p className="text-sm font-medium">Como ficaria o tema</p>
        </div>

        {/* Botão de exemplo */}
        <div
          style={{
            backgroundColor: colorValue,
            color: '#000000',
          }}
          className="rounded-xl px-4 py-2.5 text-sm font-semibold text-center transition"
        >
          Botão com cor de destaque
        </div>

        {/* Cores de texto */}
        <div className="grid grid-cols-2 gap-2">
          <div
            style={{
              backgroundColor: isDark ? '#16111f' : '#f0f0f0',
              color: isDark ? '#e2e8f0' : '#1e293b',
              borderColor: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)',
            }}
            className="rounded-lg border p-2.5 text-xs"
          >
            <p className="font-medium">Texto primário</p>
            <p className="text-[10px] opacity-60 mt-1">Descrição</p>
          </div>

          <div
            style={{
              backgroundColor: colorValue + '20',
              borderColor: colorValue,
              color: colorValue,
            }}
            className="rounded-lg border p-2.5 text-xs"
          >
            <p className="font-medium">Destaque</p>
            <p className="text-[10px] opacity-80 mt-1">Com cor</p>
          </div>
        </div>
      </div>
    </div>
  );
}
