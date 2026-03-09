import { api } from "@/services/api";
import type { ApiEnvelope } from "@/types/api";
import type { WorkflowListResponse } from "../types/workflowTypes";

const fallback: WorkflowListResponse = {
  workflows: [
    { id: "wf-01", name: "Lead Qualification", trigger: "Webhook", runsToday: 328, successRate: 99.1 },
    { id: "wf-02", name: "Ticket Escalation", trigger: "Schedule", runsToday: 114, successRate: 97.5 },
    { id: "wf-03", name: "Billing Reminder", trigger: "Event", runsToday: 48, successRate: 98.4 }
  ]
};

export async function fetchWorkflows(): Promise<WorkflowListResponse> {
  try {
    const response = await api.get<ApiEnvelope<WorkflowListResponse>>("/workflows");
    return response.data?.data ?? fallback;
  } catch {
    return fallback;
  }
}
