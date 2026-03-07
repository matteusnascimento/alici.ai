"use client";

import { create } from "zustand";
import type { BillingOverview } from "../types/billingTypes";

interface BillingState {
  loading: boolean;
  overview: BillingOverview | null;
  setOverview: (overview: BillingOverview) => void;
}

export const useBillingStore = create<BillingState>((set) => ({
  loading: true,
  overview: null,
  setOverview: (overview) => set({ overview, loading: false })
}));
