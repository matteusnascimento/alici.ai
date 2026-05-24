/**
 * Mapa de cores de destaque disponíveis
 * Mapeia nomes de cores para valores HEX
 */
export const colorMap: Record<string, string> = {
  cyan: '#6ee7f9',
  blue: '#3b82f6',
  green: '#10b981',
  orange: '#f97316',
  amber: '#fbbf24',
};

const HEX_COLOR_RE = /^#(?:[0-9a-f]{3}|[0-9a-f]{6})$/i;

function normalizeHex(value: string): string | null {
  const raw = value.trim();
  if (!HEX_COLOR_RE.test(raw)) {
    return null;
  }

  if (raw.length === 4) {
    const [, r, g, b] = raw;
    return `#${r}${r}${g}${g}${b}${b}`.toLowerCase();
  }

  return raw.toLowerCase();
}

/**
 * Obtém o valor HEX de uma cor pelo nome
 */
export function getColorValue(colorName: string): string {
  return normalizeHex(colorName) || colorMap[colorName] || colorMap.cyan;
}

export function getColorRgbTriplet(colorName: string): string {
  const hex = getColorValue(colorName).replace('#', '');
  const value = Number.parseInt(hex, 16);
  const r = (value >> 16) & 255;
  const g = (value >> 8) & 255;
  const b = value & 255;

  return `${r} ${g} ${b}`;
}

/**
 * Lista todas as cores disponíveis
 */
export function getAvailableColors(): string[] {
  return Object.keys(colorMap);
}
