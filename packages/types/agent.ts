export type Agent = {
  id: string
  organization_id: string
  name: string
  system_prompt: string
  model: string
  tools: Record<string, unknown>
}
