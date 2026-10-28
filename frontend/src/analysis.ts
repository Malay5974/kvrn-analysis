import type { AnalysisPoint } from "./api";

export interface DailyError { date: string; label: string; mae: number; bias: number }

export function aggregateDailyErrors(points: AnalysisPoint[]): DailyError[] {
  const days = new Map<string, { absolute: number; signed: number; count: number }>();
  for (const point of points) {
    if (point.error_mw === null || point.absolute_error_mw === null) continue;
    const date = point.delivery_time.slice(0, 10);
    const current = days.get(date) ?? { absolute: 0, signed: 0, count: 0 };
    current.absolute += point.absolute_error_mw;
    current.signed += point.error_mw;
    current.count += 1;
    days.set(date, current);
  }
  return [...days.entries()].map(([date, value]) => ({
    date,
    label: new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short" }).format(new Date(`${date}T00:00:00Z`)),
    mae: value.absolute / value.count,
    bias: value.signed / value.count,
  }));
}

export function formatMw(value: number | null): string {
  return value === null ? "—" : `${new Intl.NumberFormat("en-GB", { maximumFractionDigits: 0 }).format(value)} MW`;
}

export function formatPercent(value: number | null): string {
  return value === null ? "—" : `${value.toFixed(1)}%`;
}

export function formatChartTime(value: string): string {
  return new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short", hour: "2-digit", hour12: false, timeZone: "UTC" }).format(new Date(value));
}
