# Demo Video Script

Target length: 8–9 minutes. Maximum allowed length: 10 minutes.

Before recording:

1. Open https://kvrn-analysis-web.vercel.app in an incognito window.
2. Keep the GitHub repository and API documentation open in separate tabs.
3. Set the dashboard to 1–31 January 2026 and the EPEX hourly profile.
4. Record at 1080p with browser zoom at 100%.
5. Do not show passwords, tokens, email inboxes, or private browser tabs.

## Part 1 — Customer pilot presentation (0:00–4:20)

### 0:00–0:35 — Customer problem and pilot outcome

> This pilot helps a UK utility's day-ahead purchasing team understand the wind-generation
> forecast that was actually available when they had to buy power. It also quantifies how far
> that forecast differed from actual wind generation, allowing buyers to include forecast risk
> in procurement decisions.

Show the dashboard title and decision-context panel.

### 0:35–1:20 — Decision-safe forecast selection

> The default profile represents the EPEX hourly day-ahead decision. For every delivery day,
> the application selects the latest Elexon forecast published by 09:20 London time on the
> previous day. Forecasts published after that cutoff are deliberately excluded, preventing
> future-data leakage and reproducing the information available to the buyer.

Point to the market selector, date range, cutoff time, and timezone.

### 1:20–2:05 — Forecast and actual generation

Show the forecast-versus-actual chart.

> The blue series is the decision-time forecast and the comparison series is actual national
> wind generation. Elexon forecasts are hourly, while actuals are half-hourly, so the application
> averages each pair of actual readings into an hourly value before comparison.

Hover over two or three chart points to demonstrate exact values and timestamps.

### 2:05–3:05 — Accuracy metrics

Point to each metric card.

> Mean absolute error shows the typical size of a forecast miss in megawatts. RMSE gives more
> weight to large misses. Bias uses forecast minus actual: positive bias means the forecast was
> generally too high, which could cause the team to procure too little additional power. WAPE
> expresses total absolute error relative to total actual generation and makes the magnitude
> easier to communicate.

Mention that the January EPEX view contains 744 complete hourly pairs with no missing values.

### 3:05–3:45 — Daily bias and operational use

Show the daily error/bias chart and buyer-facing interpretation.

> This view shows when forecast error was concentrated. A buyer could combine expected demand
> with the selected wind forecast, then apply an evidence-based risk margin informed by the
> historical error distribution. The product supports the decision; it does not automatically
> execute a trade.

### 3:45–4:20 — Data quality and alternate market profile

Show the coverage section and briefly switch to the N2EX profile.

> Coverage is explicit so a buyer can see whether the analysis is complete. The alternate N2EX
> profile uses its later decision cutoff, demonstrating that forecast selection is driven by the
> real decision context rather than one hard-coded timestamp.

Return to the EPEX profile before moving to Part 2.

## Part 2 — Technical lead handover (4:20–8:40)

### 4:20–5:00 — Architecture

Show the repository tree and README.

> The system is split into a React and TypeScript frontend and a FastAPI backend. The browser
> calls a typed analysis API. The backend retrieves Elexon WINDFOR forecasts and FUELHH actuals,
> applies the decision rule and resolution alignment, calculates metrics, and returns a single
> analysis response. Both applications are independently deployed on Vercel and can also run
> together through Docker Compose.

### 5:00–5:50 — Backend design

Open `backend/app` and briefly show `clients`, `domain`, `services`, `api.py`, and `models.py`.

> The Elexon client owns asynchronous HTTP access, timeouts, and bounded retries. Pure domain
> functions own cutoff calculation, eligible forecast selection, hourly alignment, and metrics.
> The service layer orchestrates retrieval and analysis, while the API layer validates inputs
> and exposes stable response models. This separation keeps the decision logic independently
> testable.

### 5:50–6:40 — Core correctness rules

Show the relevant domain code and tests.

> The key correctness rule is publish-time eligibility: only forecasts published at or before
> the previous day's market cutoff may be selected. Times are timezone-aware, using London time
> for the market decision and UTC for Elexon timestamps. Actual half-hour records are grouped
> into hourly means. Error is consistently defined as forecast minus actual. Missing and duplicate
> records are tracked rather than silently discarded.

### 6:40–7:20 — Frontend and performance

Show `frontend/src/App.tsx`, `api.ts`, and the chart components.

> The frontend uses TanStack Query for request state and caching, typed API contracts, responsive
> layouts, explicit loading and failure states, and lazy-loaded chart components. Filters become
> API query parameters, so calculations remain centralized in the backend instead of being
> duplicated in the browser.

### 7:20–8:00 — Tests and engineering discipline

Show `TESTING.md` and the test directories.

> Backend tests cover decision cutoffs, forecast eligibility, aggregation, metrics, retry behavior,
> API validation, and CORS. Frontend tests cover analysis helpers and user-visible dashboard states.
> Linting and production builds are part of the validation workflow. The repository also contains
> Dockerfiles, Docker Compose, environment-based configuration, and a detailed manual test plan.

### 8:00–8:40 — Deployment, limitations, and next steps

Show the Vercel URLs and API documentation.

> The pilot is publicly deployed with separate frontend and API projects. The main limitations are
> that it analyzes national wind only, covers January 2026 for this challenge, and uses historical
> forecast error rather than a probabilistic forecasting model. Logical next steps are demand data,
> portfolio-level generation, configurable auction products, persistent analysis snapshots,
> probabilistic risk bands, authentication, observability, and CI deployment checks.

End on the live dashboard and stop recording before 10:00.

## Upload settings

- Visibility: Unlisted
- Title: `Wind Decision Intelligence — Pilot Demo and Technical Handover`
- Description: include the live application URL and public repository URL
- Verify the final video URL in an incognito window before submission
