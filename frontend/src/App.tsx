import { lazy, Suspense, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Activity, AlertTriangle, ArrowDownRight, ArrowUpRight, CalendarDays, CheckCircle2, Clock3, Database, Gauge, RefreshCw, Wind } from "lucide-react";
import { fetchAnalysis, fetchMarketProfiles, type AnalysisFilters, type MarketProfileName } from "./api";
import { aggregateDailyErrors, formatMw, formatPercent } from "./analysis";
import { DashboardSkeleton } from "./components/DashboardSkeleton";
import { MetricCard } from "./components/MetricCard";

const DEFAULT_FILTERS: AnalysisFilters = { deliveryFrom: "2026-01-01", deliveryTo: "2026-01-31", marketProfile: "epex_hourly" };
const ForecastChart = lazy(() => import("./components/ForecastChart").then((module) => ({ default: module.ForecastChart })));
const ErrorChart = lazy(() => import("./components/ErrorChart").then((module) => ({ default: module.ErrorChart })));

export default function App() {
  const [draftFilters, setDraftFilters] = useState(DEFAULT_FILTERS);
  const [filters, setFilters] = useState(DEFAULT_FILTERS);
  const profiles = useQuery({ queryKey: ["market-profiles"], queryFn: ({ signal }) => fetchMarketProfiles(signal) });
  const analysis = useQuery({ queryKey: ["analysis", filters], queryFn: ({ signal }) => fetchAnalysis(filters, signal) });
  const dailyErrors = useMemo(() => aggregateDailyErrors(analysis.data?.points ?? []), [analysis.data?.points]);
  const filtersChanged = JSON.stringify(draftFilters) !== JSON.stringify(filters);

  function updateFilter<Key extends keyof AnalysisFilters>(key: Key, value: AnalysisFilters[Key]) {
    setDraftFilters((current) => ({ ...current, [key]: value }));
  }

  return <div className="app-shell">
    <header className="topbar">
      <a className="brand" href="#top" aria-label="Wind Decision Intelligence home"><span className="brand__mark"><Wind size={19} /></span><span>Wind Decision <strong>Intelligence</strong></span></a>
      <div className="topbar__status"><span className="live-dot" />Elexon data · January 2026</div>
    </header>
    <main id="top">
      <section className="hero">
        <div><p className="eyebrow">DAY-AHEAD PROCUREMENT · PILOT ANALYSIS</p><h1>Know the forecast.<br /><em>Price the uncertainty.</em></h1><p className="hero__intro">A decision-time view of national wind generation—using only the information available before the market closed.</p></div>
        <div className="hero__meta"><Clock3 size={18} /><div><span>Default decision gate</span><strong>09:20 · D−1</strong></div></div>
      </section>
      <section className="control-panel" aria-label="Analysis controls">
        <label><span><CalendarDays size={15} /> From</span><input aria-label="From date" type="date" min="2026-01-01" max={draftFilters.deliveryTo} value={draftFilters.deliveryFrom} onChange={(event) => updateFilter("deliveryFrom", event.target.value)} /></label>
        <label><span><CalendarDays size={15} /> To</span><input aria-label="To date" type="date" min={draftFilters.deliveryFrom} max="2026-01-31" value={draftFilters.deliveryTo} onChange={(event) => updateFilter("deliveryTo", event.target.value)} /></label>
        <label className="control-panel__market"><span><Clock3 size={15} /> Market gate</span><select aria-label="Market gate" value={draftFilters.marketProfile} onChange={(event) => updateFilter("marketProfile", event.target.value as MarketProfileName)}>{(profiles.data ?? []).map((profile) => <option key={profile.name} value={profile.name}>{profile.label}</option>)}{!profiles.data && <option value="epex_hourly">EPEX hourly day-ahead</option>}</select></label>
        <button className="primary-button" disabled={!filtersChanged || analysis.isFetching} onClick={() => setFilters(draftFilters)}>{analysis.isFetching ? <RefreshCw size={16} className="spin" /> : <Activity size={16} />}Apply analysis</button>
      </section>
      {analysis.isLoading && <DashboardSkeleton />}
      {analysis.isError && <section className="error-state" role="alert"><AlertTriangle size={24} /><div><h2>We couldn’t load the analysis</h2><p>{analysis.error.message}</p></div><button onClick={() => analysis.refetch()}><RefreshCw size={16} /> Try again</button></section>}
      {analysis.data && <>
        <section className="decision-strip"><div><span className="decision-strip__icon"><CheckCircle2 size={18} /></span><div><span>Decision context</span><strong>{analysis.data.market_profile.label}</strong></div></div><p>Latest eligible forecast at or before <strong>{analysis.data.market_profile.cutoff_local_time.slice(0, 5)}</strong> London time on D−1. No future information included.</p><span className="quality-badge">{analysis.data.coverage.complete_pairs}/{analysis.data.coverage.expected_hours} hours complete</span></section>
        <section className="metric-grid" aria-label="Forecast accuracy metrics">
          <MetricCard icon={Gauge} label="Mean absolute error" value={formatMw(analysis.data.metrics.mae_mw)} description="Typical hourly forecast miss" />
          <MetricCard icon={Activity} label="Root mean square error" value={formatMw(analysis.data.metrics.rmse_mw)} description="Penalises the largest misses" />
          <MetricCard icon={ArrowUpRight} label="Forecast bias" value={formatMw(analysis.data.metrics.bias_mw)} description="Positive means over-forecasting" tone="warning" />
          <MetricCard icon={Database} label="Weighted absolute error" value={formatPercent(analysis.data.metrics.wape_percent)} description="Error relative to actual output" />
        </section>
        <section className="panel panel--wide"><div className="panel__header"><div><p className="section-label">GENERATION PROFILE</p><h2>Forecast versus actual wind</h2><p>Hourly forecast at the decision gate compared with mean half-hourly outturn.</p></div><span className="unit-pill">MW · UTC</span></div><Suspense fallback={<div className="chart-loading">Preparing chart…</div>}><ForecastChart points={analysis.data.points} /></Suspense></section>
        <section className="insight-grid">
          <article className="panel"><div className="panel__header"><div><p className="section-label">DIRECTION OF ERROR</p><h2>Daily forecast bias</h2><p>Above zero means forecast generation exceeded actual output.</p></div></div><Suspense fallback={<div className="chart-loading">Preparing chart…</div>}><ErrorChart days={dailyErrors} /></Suspense></article>
          <article className="panel bias-panel"><p className="section-label">BUYER TAKEAWAY</p><div className="bias-panel__icon"><ArrowUpRight size={24} /></div><h2>Wind was over-forecast in {formatPercent(analysis.data.metrics.over_forecast_percent)} of hours.</h2><p>The selected day-ahead forecast carried an average positive bias of <strong>{formatMw(analysis.data.metrics.bias_mw)}</strong>. A buyer relying on the point forecast alone would frequently risk under-procuring firm power.</p><div className="split-stat"><div><ArrowUpRight size={17} /><span>Over-forecast<strong>{formatPercent(analysis.data.metrics.over_forecast_percent)}</strong></span></div><div><ArrowDownRight size={17} /><span>Under-forecast<strong>{formatPercent(analysis.data.metrics.under_forecast_percent)}</strong></span></div></div></article>
        </section>
        <section className="data-note"><Database size={19} /><div><strong>Complete source coverage</strong><p>{analysis.data.data_quality.actual_source_records.toLocaleString("en-GB")} actual records and {analysis.data.data_quality.forecast_source_records.toLocaleString("en-GB")} forecast records reviewed. Actuals are averaged from two half-hour periods. Error is forecast minus actual.</p></div><span>{analysis.data.data_quality.warnings.length === 0 ? "No quality warnings" : `${analysis.data.data_quality.warnings.length} warnings`}</span></section>
      </>}
    </main>
    <footer><span>Contains BMRS data © Elexon Limited</span><span>Decision intelligence pilot · January 2026</span></footer>
  </div>;
}
