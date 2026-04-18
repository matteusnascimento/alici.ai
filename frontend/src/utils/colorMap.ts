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

/**
 * Obtém o valor HEX de uma cor pelo nome
 */
export function getColorValue(colorName: string): string {
  return colorMap[colorName] || colorMap.cyan;
}

/**
 * Lista todas as cores disponíveis
 */
export function getAvailableColors(): string[] {
  return Object.keys(colorMap);
}
