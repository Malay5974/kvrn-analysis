import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";
import type { AnalysisResponse } from "./api";

const response: AnalysisResponse = {
  delivery_from: "2026-01-01", delivery_to: "2026-01-01",
  market_profile: { name: "epex_hourly", label: "EPEX hourly day-ahead", cutoff_local_time: "09:20:00", timezone: "Europe/London", product_resolution_minutes: 60, description: "Test" },
  units: "MW", error_definition: "forecast - actual", actual_resolution: "Hourly mean",
  metrics: { observations: 1, mae_mw: 100, rmse_mw: 100, bias_mw: 100, wape_percent: 10, over_forecast_percent: 80, under_forecast_percent: 20 },
  coverage: { expected_hours: 1, complete_pairs: 1, missing_forecasts: 0, missing_actuals: 0 },
  data_quality: { actual_source_records: 2, forecast_source_records: 4, duplicate_actual_records: 0, duplicate_forecast_records: 0, warnings: [] },
  points: [{ delivery_time: "2026-01-01T00:00:00Z", decision_cutoff: "2025-12-31T09:20:00Z", forecast_publish_time: "2025-12-31T07:30:00Z", forecast_mw: 1100, actual_mw: 1000, error_mw: 100, absolute_error_mw: 100, status: "complete" }],
};

function renderApp() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={client}><App /></QueryClientProvider>);
}

describe("dashboard", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn((input: RequestInfo | URL) => {
      const payload = String(input).includes("market-profiles") ? [response.market_profile] : response;
      return Promise.resolve(new Response(JSON.stringify(payload), { status: 200, headers: { "Content-Type": "application/json" } }));
    }));
  });
  afterEach(() => vi.unstubAllGlobals());

  it("renders metrics and buyer takeaway", async () => {
    renderApp();
    expect(await screen.findAllByText("100 MW")).toHaveLength(4);
    expect(screen.getByText(/Wind was over-forecast in 80.0%/)).toBeInTheDocument();
    expect(screen.getByText("1/1 hours complete")).toBeInTheDocument();
  });

  it("enables apply after a date changes", async () => {
    const user = userEvent.setup(); renderApp();
    await screen.findByText("1/1 hours complete");
    const button = screen.getByRole("button", { name: /Apply analysis/ });
    expect(button).toBeDisabled();
    await user.clear(screen.getByLabelText("From date"));
    await user.type(screen.getByLabelText("From date"), "2026-01-02");
    expect(button).toBeEnabled();
  });
});
