"use client";

import { create } from "zustand";
import type { BillingOverview } from "../types/billingTypes";

interface BillingState {
  loading: boolean;
  actionLoading: boolean;
  error: string | null;
  overview: BillingOverview | null;
  setLoading: (loading: boolean) => void;
  setActionLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setOverview: (overview: BillingOverview) => void;
}

export const useBillingStore = create<BillingState>((set) => ({
  loading: true,
  actionLoading: false,
  error: null,
  overview: null,
  setLoading: (loading) => set({ loading }),
  setActionLoading: (actionLoading) => set({ actionLoading }),
  setError: (error) => set({ error }),
  setOverview: (overview) => set({ overview, loading: false, error: null })
}));
