export interface PlanInfo {
  name: string;
  priceMonthly: number;
  seats: number;
}

export interface InvoiceItem {
  id: string;
  period: string;
  amount: number;
  status: "paid" | "pending";
}

export interface BillingOverview {
  plan: PlanInfo;
  invoices: InvoiceItem[];
}
