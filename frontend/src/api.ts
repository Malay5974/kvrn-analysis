export type MarketProfileName = "epex_hourly" | "n2ex_hourly";

export interface MarketProfile {
  name: MarketProfileName;
  label: string;
  cutoff_local_time: string;
  timezone: string;
  product_resolution_minutes: number;
  description: string;
}

export interface AnalysisPoint {
  delivery_time: string;
  decision_cutoff: string;
  forecast_publish_time: string | null;
  forecast_mw: number | null;
  actual_mw: number | null;
  error_mw: number | null;
  absolute_error_mw: number | null;
  status: "complete" | "missing_forecast" | "missing_actual";
}

export interface AnalysisResponse {
  delivery_from: string;
  delivery_to: string;
  market_profile: MarketProfile;
  units: string;
  error_definition: string;
  actual_resolution: string;
  metrics: {
    observations: number;
    mae_mw: number | null;
    rmse_mw: number | null;
    bias_mw: number | null;
    wape_percent: number | null;
    over_forecast_percent: number | null;
    under_forecast_percent: number | null;
  };
  coverage: { expected_hours: number; complete_pairs: number; missing_forecasts: number; missing_actuals: number };
  data_quality: {
    actual_source_records: number;
    forecast_source_records: number;
    duplicate_actual_records: number;
    duplicate_forecast_records: number;
    warnings: string[];
  };
  points: AnalysisPoint[];
}

export interface AnalysisFilters {
  deliveryFrom: string;
  deliveryTo: string;
  marketProfile: MarketProfileName;
}

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, { signal });
  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(body?.detail ?? `Request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function fetchMarketProfiles(signal?: AbortSignal): Promise<MarketProfile[]> {
  return request("/api/v1/market-profiles", signal);
}

export function fetchAnalysis(filters: AnalysisFilters, signal?: AbortSignal): Promise<AnalysisResponse> {
  const query = new URLSearchParams({
    delivery_from: filters.deliveryFrom,
    delivery_to: filters.deliveryTo,
    market_profile: filters.marketProfile,
  });
  return request(`/api/v1/analysis?${query}`, signal);
}
