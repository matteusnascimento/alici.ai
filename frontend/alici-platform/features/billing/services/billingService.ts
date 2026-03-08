import { api } from "@/services/api";
import type { BillingActionResult, BillingOverview, InvoiceItem } from "../types/billingTypes";

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
    const [plansResponse, subscriptionResponse] = await Promise.all([
      api.get("/billing/plans"),
      api.get("/billing/subscription")
    ]);

    const plansData = plansResponse.data?.data ?? plansResponse.data;
    const subscriptionData = subscriptionResponse.data?.data ?? subscriptionResponse.data;

    const plans = plansData?.plans || {};
    const currentPlan = subscriptionData?.plan || "free";
    const currentPlanInfo = plans[currentPlan] || { name: "Free", price: 0 };

    const seatsByPlan: Record<string, number> = {
      free: 1,
      pro: 5,
      enterprise: 25
    };

    const invoices: InvoiceItem[] = Array.isArray(subscriptionData?.history)
      ? subscriptionData.history
      : [];

    return {
      plan: {
        name: currentPlanInfo.name || "Free",
        priceMonthly: Number(currentPlanInfo.price) || 0,
        seats: seatsByPlan[currentPlan] || 1
      },
      invoices
    };
  } catch {
    return fallback;
  }
}

export async function subscribePlan(plan: "pro" | "enterprise"): Promise<BillingActionResult> {
  const response = await api.post("/billing/checkout", { plan });
  const data = response.data?.data ?? response.data;
  return {
    message: "Checkout iniciado",
    checkoutUrl: data?.checkout_url
  };
}

export async function cancelPlan(): Promise<BillingActionResult> {
  const response = await api.post("/billing/subscription/cancel", { immediate: false });
  const data = response.data?.data ?? response.data;
  return {
    message: data?.message || "Cancelamento solicitado"
  };
}
