import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { useBilling } from "./useBilling";
import { useBillingStore } from "../store/billingStore";
import * as billingService from "../services/billingService";
import type { BillingOverview } from "../types/billingTypes";

vi.mock("../services/billingService", () => ({
  fetchBillingOverview: vi.fn(),
  subscribePlan: vi.fn(),
  cancelPlan: vi.fn()
}));

const initialOverview: BillingOverview = {
  plan: { name: "Free", priceMonthly: 0, seats: 1 },
  invoices: []
};

const proOverview: BillingOverview = {
  plan: { name: "Pro", priceMonthly: 99, seats: 5 },
  invoices: [{ id: "inv-01", period: "2026-03", amount: 99, status: "paid" }]
};

const fetchBillingOverviewMock = vi.mocked(billingService.fetchBillingOverview);
const subscribePlanMock = vi.mocked(billingService.subscribePlan);
const cancelPlanMock = vi.mocked(billingService.cancelPlan);

describe("useBilling", () => {
  beforeEach(() => {
    useBillingStore.setState({
      loading: true,
      actionLoading: false,
      error: null,
      overview: null
    });
    vi.clearAllMocks();
  });

  afterEach(() => {
    useBillingStore.setState({
      loading: true,
      actionLoading: false,
      error: null,
      overview: null
    });
  });

  it("runs upgrade flow and refreshes overview", async () => {
    fetchBillingOverviewMock.mockResolvedValueOnce(initialOverview).mockResolvedValueOnce(proOverview);
    subscribePlanMock.mockResolvedValue({ message: "Checkout iniciado" });

    const { result } = renderHook(() => useBilling());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    await act(async () => {
      await result.current.upgrade("pro");
    });

    expect(subscribePlanMock).toHaveBeenCalledWith("pro");
    expect(result.current.overview?.plan.name).toBe("Pro");
    expect(result.current.actionLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it("sets error when upgrade fails", async () => {
    fetchBillingOverviewMock.mockResolvedValueOnce(initialOverview);
    subscribePlanMock.mockRejectedValue(new Error("network"));

    const { result } = renderHook(() => useBilling());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    let thrown: unknown;
    await act(async () => {
      try {
        await result.current.upgrade("enterprise");
      } catch (error) {
        thrown = error;
      }
    });

    expect((thrown as Error).message).toBe("upgrade_failed");
    await waitFor(() => {
      expect(result.current.error).toBe("Failed to start upgrade flow");
      expect(result.current.actionLoading).toBe(false);
    });
  });

  it("runs cancel flow and refreshes overview", async () => {
    fetchBillingOverviewMock.mockResolvedValueOnce(proOverview).mockResolvedValueOnce(initialOverview);
    cancelPlanMock.mockResolvedValue({ message: "Cancelamento solicitado" });

    const { result } = renderHook(() => useBilling());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    await act(async () => {
      await result.current.cancelSubscription();
    });

    expect(cancelPlanMock).toHaveBeenCalledTimes(1);
    expect(result.current.overview?.plan.name).toBe("Free");
    expect(result.current.actionLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it("sets error when cancel fails", async () => {
    fetchBillingOverviewMock.mockResolvedValueOnce(proOverview);
    cancelPlanMock.mockRejectedValue(new Error("network"));

    const { result } = renderHook(() => useBilling());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    let thrown: unknown;
    await act(async () => {
      try {
        await result.current.cancelSubscription();
      } catch (error) {
        thrown = error;
      }
    });

    expect((thrown as Error).message).toBe("cancel_failed");
    await waitFor(() => {
      expect(result.current.error).toBe("Failed to cancel subscription");
      expect(result.current.actionLoading).toBe(false);
    });
  });
});
