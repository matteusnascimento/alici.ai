export function parseBearer(header?: string): string | null {
  if (!header || !header.startsWith("Bearer ")) return null
  return header.slice(7)
}
