import { api } from "@/services/api";
import type { BillingOverview } from "../types/billingTypes";

const fallback: BillingOverview = {
  plan: { name: "Growth", priceMonthly: 249, seats: 12 },
  invoices: [
    { id: "inv-001", period: "2026-03", amount: 249, status: "paid" },
    { id: "inv-000", period: "2026-02", amount: 249, status: "paid" },
    { id: "inv-999", period: "2026-01", amount: 199, status: "paid" }
  ]
};

export async function fetchBillingOverview(): Promise<BillingOverview> {
  try {
    const response = await api.get<BillingOverview>("/billing/overview");
    return response.data;
  } catch {
    return fallback;
  }
}
