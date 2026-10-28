import { describe, expect, it } from "vitest";
import { aggregateDailyErrors, formatMw, formatPercent } from "./analysis";
import type { AnalysisPoint } from "./api";

const point: AnalysisPoint = { delivery_time: "2026-01-01T00:00:00Z", decision_cutoff: "2025-12-31T09:20:00Z", forecast_publish_time: "2025-12-31T07:30:00Z", forecast_mw: 120, actual_mw: 100, error_mw: 20, absolute_error_mw: 20, status: "complete" };

describe("analysis helpers", () => {
  it("aggregates daily errors", () => {
    const result = aggregateDailyErrors([point, { ...point, delivery_time: "2026-01-01T01:00:00Z", error_mw: -10, absolute_error_mw: 10 }]);
    expect(result[0]).toMatchObject({ mae: 15, bias: 5 });
  });
  it("formats values", () => {
    expect(formatMw(null)).toBe("—"); expect(formatMw(2142.4)).toBe("2,142 MW"); expect(formatPercent(18.497)).toBe("18.5%");
  });
});
