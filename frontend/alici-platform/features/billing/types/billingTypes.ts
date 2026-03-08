export interface PlanInfo {
  name: string;
  priceMonthly: number;
  seats: number;
}

export interface InvoiceItem {
  id: string;
  period: string;
  amount: number;
  status: "paid" | "pending" | "failed" | "canceled";
}

export interface BillingOverview {
  plan: PlanInfo;
  invoices: InvoiceItem[];
}

export interface BillingActionResult {
  message: string;
  checkoutUrl?: string;
}
