export interface WorkflowItem {
  id: string;
  name: string;
  trigger: string;
  runsToday: number;
  successRate: number;
}

export interface WorkflowListResponse {
  workflows: WorkflowItem[];
}
