export type Workflow = {
  id: string
  organization_id: string
  name: string
  graph: {
    nodes: Array<{ id: string; type: string; data: Record<string, unknown> }>
    edges: Array<{ id: string; source: string; target: string }>
  }
  is_active: boolean
}
