# End-to-End Test Plan

## Purpose

This document is the manual acceptance test plan for the Wind Decision Intelligence pilot.
It covers the React dashboard, FastAPI backend, Elexon integration, analytical correctness,
error handling, responsive layouts, accessibility, and final submission readiness.

Record each result as `PASS`, `FAIL`, or `BLOCKED`. For failures, capture a screenshot and
copy any relevant browser-console or server-log message into the Notes column.

## Test environment

| Item | Value |
|---|---|
| Frontend | <https://kvrn-analysis-web.vercel.app> |
| Backend health | <https://kvrn-analysis-api.vercel.app/health> |
| API documentation | <https://kvrn-analysis-api.vercel.app/docs> |
| Supported delivery period | 1–31 January 2026 |
| Default market profile | EPEX hourly day-ahead |
| Default decision cutoff | 09:20 Europe/London on D−1 |
| Actual source | Elexon FUELHH, WIND |
| Forecast source | Elexon WINDFOR |

Tester:

```text
Name:
Date:
Browser and version:
Operating system:
```

## Optional local-development setup

The acceptance tests below use the deployed Vercel environment. Start the local services only
when validating local-development behavior or changes that have not yet been deployed.

### Start the backend

```bash
cd /Users/malaydelwadiya/Desktop/GridBricks/backend
source .venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Start the frontend

In a second terminal:

```bash
cd /Users/malaydelwadiya/Desktop/GridBricks/frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

### Run automated checks

```bash
cd /Users/malaydelwadiya/Desktop/GridBricks
backend/.venv/bin/pytest -q backend
backend/.venv/bin/ruff check backend

cd frontend
npm run test
npm run lint
npm run build
```

Expected automated results:

- Backend: 10 tests passed.
- Frontend: 4 tests passed.
- Backend and frontend lint: no errors.
- Frontend production build: successful.

## Reference calculations

### Full January — EPEX hourly

| Result | Expected value |
|---|---:|
| Date range | 1–31 January 2026 |
| Decision cutoff | 09:20 D−1 |
| Selected forecast publication | 07:30 D−1 |
| Expected hours | 744 |
| Complete hours | 744 |
| MAE | approximately 2,142 MW |
| RMSE | approximately 2,612 MW |
| Bias | approximately +1,852 MW |
| WAPE | approximately 18.5% |
| Over-forecast intervals | approximately 85.1% |
| Under-forecast intervals | approximately 14.9% |

### 10–12 January — N2EX hourly

| Result | Expected value |
|---|---:|
| Date range | 10–12 January 2026 |
| Decision cutoff | 09:50 D−1 |
| Selected forecast publication | 09:30 D−1 |
| Expected hours | 72 |
| Complete hours | 72 |
| MAE | approximately 3,633 MW |
| RMSE | approximately 4,204 MW |
| Bias | approximately +3,237 MW |
| WAPE | approximately 29.6% |
| Over-forecast intervals | approximately 86.1% |

Display values may differ by one MW or 0.1 percentage points due to rounding.

---

## Functional test cases

### TC-001 — Backend health

**Priority:** Critical

1. Open <https://kvrn-analysis-api.vercel.app/health>.

Expected:

- HTTP status is `200`.
- Response is `{"status":"ok"}`.

| Result | Notes/evidence |
|---|---|
|  |  |

### TC-002 — Initial dashboard load

**Priority:** Critical

1. Open <https://kvrn-analysis-web.vercel.app> in a fresh browser tab.
2. Wait for the initial request to finish.

Expected:

- Loading placeholders appear temporarily.
- No blank screen or error panel remains.
- Default dates are 1–31 January 2026.
- Default market is EPEX hourly day-ahead.
- Apply Analysis is initially disabled.
- Coverage shows `744/744 hours complete`.
- Values match the full-January EPEX reference calculations above.

| Result | Notes/evidence |
|---|---|
|  |  |

### TC-003 — Decision context

**Priority:** Critical

Expected:

- Market context says `EPEX hourly day-ahead`.
- Decision cutoff is `09:20` London time on D−1.
- The interface states that no future information is included.
- Units are shown as MW.
- Coverage is visible.

| Result | Notes/evidence |
|---|---|
|  |  |

### TC-004 — Accuracy metric cards

**Priority:** Critical

Expected:

- MAE, RMSE, bias, and WAPE cards are visible.
- Each value has a descriptive label.
- Bias explains that a positive value means over-forecasting.
- No value shows `NaN`, `undefined`, `null`, or an invalid unit.

| Result | Notes/evidence |
|---|---|
|  |  |

### TC-005 — Forecast-versus-actual chart

**Priority:** High

1. Locate the Forecast versus actual wind chart.
2. Hover over several locations.

Expected:

- Forecast line is orange/brown.
- Actual line is green.
- Legend identifies both series.
- Tooltip shows date, time, and MW values.
- Horizontal axis shows time and vertical axis represents MW.
- Lines and tooltips are not clipped.
- There are no unexpected gaps for the complete January dataset.

| Result | Notes/evidence |
|---|---|
|  |  |

### TC-006 — Daily forecast-bias chart

**Priority:** High

1. Locate the Daily forecast bias chart.
2. Hover over positive and negative bars.

Expected:

- A bar appears for every selected day.
- Positive bias is orange and negative bias is green.
- Tooltip displays daily bias in MW.
- The zero-reference line is visible.
- Labels remain readable.

| Result | Notes/evidence |
|---|---|
|  |  |

### TC-007 — Buyer takeaway

**Priority:** High

Expected for the full-month EPEX selection:

- The interface states that wind was over-forecast in approximately 85.1% of hours.
- Positive bias is explained in customer language.
- The text connects over-forecasting with under-procurement risk.
- Over-forecast and under-forecast percentages total approximately 100%.

| Result | Notes/evidence |
|---|---|
|  |  |

### TC-008 — Three-day EPEX filter

**Priority:** Critical

1. Set From to 10 January 2026.
2. Set To to 12 January 2026.
3. Keep EPEX hourly day-ahead selected.
4. Click Apply Analysis.

Expected:

- Apply becomes enabled after the date changes.
- A loading indicator appears while the request runs.
- Apply cannot be repeatedly activated while loading.
- Coverage becomes `72/72 hours complete`.
- Both charts show only 10–12 January.
- Cutoff remains `09:20`.
- All metric cards and buyer-takeaway values update together.

| Result | Notes/evidence |
|---|---|
|  |  |

### TC-009 — Three-day N2EX filter

**Priority:** Critical

1. Keep the date range at 10–12 January.
2. Select N2EX hourly day-ahead.
3. Click Apply Analysis.

Expected:

- Decision context changes to N2EX.
- Cutoff changes to `09:50`.
- Coverage remains `72/72`.
- Results match the 10–12 January N2EX reference calculations above.
- Metrics, charts, and buyer takeaway all update.

| Result | Notes/evidence |
|---|---|
|  |  |

### TC-010 — Switch back to EPEX

**Priority:** High

1. Change N2EX back to EPEX.
2. Click Apply Analysis.

Expected:

- Cutoff returns to `09:20`.
- Values change from the N2EX results.
- N2EX values do not remain in any card, chart, or explanation.

| Result | Notes/evidence |
|---|---|
|  |  |

### TC-011 — Single-day analysis

**Priority:** High

1. Set both dates to 15 January 2026.
2. Apply the analysis.

Expected:

- Coverage is `24/24 hours complete`.
- Main chart represents one day.
- Daily bias chart contains one bar.
- Metrics use 24 observations.

Repeat for 1 January and 31 January.

| Result | Notes/evidence |
|---|---|
|  |  |

### TC-012 — Date boundaries

**Priority:** High

Expected:

- Dates before 1 January cannot be selected.
- Dates after 31 January cannot be selected.
- From cannot be after To.
- To cannot be before From.
- Apply remains disabled if nothing changed.
- Apply becomes enabled after a valid filter change.

| Result | Notes/evidence |
|---|---|
|  |  |

### TC-013 — Query caching and repeated filters

**Priority:** Medium

1. Apply 10–12 January EPEX.
2. Apply 15–17 January EPEX.
3. Return to 10–12 January EPEX.

Expected:

- Each range shows the correct values.
- Old chart data does not remain after switching.
- Previously requested combinations return quickly from the frontend cache.
- No infinite request loop occurs.

| Result | Notes/evidence |
|---|---|
|  |  |

### TC-014 — Backend failure state

**Priority:** Critical

1. Stop the backend using `Control+C` in its terminal.
2. Change a filter to a range not previously loaded, then apply it.

Expected:

- The frontend does not become blank.
- A clear error panel appears.
- A Try Again button appears.
- Fake zero metrics are not displayed.

| Result | Notes/evidence |
|---|---|
|  |  |

### TC-015 — Recovery after backend restart

**Priority:** Critical

1. Restart the backend.
2. Click Try Again.

Expected:

- Dashboard recovers without restarting the frontend.
- Error panel disappears.
- Metrics and charts display the requested range.

| Result | Notes/evidence |
|---|---|
|  |  |

### TC-016 — Hard refresh and CORS

**Priority:** Critical

1. Press `Cmd + Shift + R`.

Expected:

- Dashboard loads successfully.
- No CORS message appears.
- API requests return `200`.
- Default analysis is displayed.

| Result | Notes/evidence |
|---|---|
|  |  |

---

## Responsive and accessibility tests

### TC-017 — Mobile viewport

**Viewport:** 390 × 844

Expected:

- No horizontal page scrollbar.
- Controls stack vertically.
- Metric cards use one column.
- Charts remain inside their containers.
- Buyer takeaway appears below the daily chart.
- Text, inputs, and buttons are not clipped.
- Footer content stacks vertically.

| Result | Notes/evidence |
|---|---|
|  |  |

### TC-018 — Tablet viewport

**Viewport:** 768 × 1024

Expected:

- Metric cards use two columns.
- Controls and charts remain readable.
- No overlap or horizontal overflow occurs.
- Buyer takeaway stacks below the chart when required.

| Result | Notes/evidence |
|---|---|
|  |  |

### TC-019 — Desktop viewport

**Viewport:** 1440 × 900

Expected:

- Four metric cards appear in one row.
- Dashboard remains centered.
- Main chart uses the available width.
- Buyer takeaway appears beside the daily-bias chart.
- Spacing is consistent and there is no clipping.

| Result | Notes/evidence |
|---|---|
|  |  |

### TC-020 — Keyboard navigation

1. Reload the dashboard.
2. Use Tab and Shift+Tab to navigate.
3. Change filters and activate Apply using the keyboard.

Expected:

- Date inputs, market selector, and Apply receive focus.
- Focus order follows visual order.
- Focus is visibly identifiable.
- Disabled Apply cannot be activated.
- Enabled Apply works with Enter or Space.

| Result | Notes/evidence |
|---|---|
|  |  |

### TC-021 — Browser zoom

Test at 100%, 150%, and 200% zoom.

Expected:

- Text remains readable.
- Controls remain usable.
- Important content is not clipped.
- Charts stay inside their containers.

| Result | Notes/evidence |
|---|---|
|  |  |

---

## Developer-tools tests

### TC-022 — Browser console

Open Developer Tools → Console.

Expected:

- No application JavaScript errors.
- No React rendering errors.
- No CORS errors.
- No repeated-request loop.
- No chart-size warning.
- No `NaN`, `undefined`, or invalid-date values.

Browser-extension messages may be ignored if they clearly do not originate from this application.

| Result | Notes/evidence |
|---|---|
|  |  |

### TC-023 — Network requests

Open Developer Tools → Network and apply new filters.

Expected:

- `/api/v1/market-profiles` returns `200`.
- `/api/v1/analysis?...` returns `200`.
- One analysis request occurs per new applied filter.
- No request loop occurs.
- Response dates and market profile match the selected controls.
- CORS allows `https://kvrn-analysis-web.vercel.app`.

| Result | Notes/evidence |
|---|---|
|  |  |

### TC-024 — API documentation

1. Open <https://kvrn-analysis-api.vercel.app/docs>.
2. Confirm the documented endpoints.
3. Execute `/health`.

Expected endpoints:

- `GET /health`
- `GET /api/v1/market-profiles`
- `GET /api/v1/analysis`

Expected `/health` result: `200` with `{"status":"ok"}`.

| Result | Notes/evidence |
|---|---|
|  |  |

### TC-025 — Invalid API inputs

Use the API documentation to request:

1. A date before January 2026.
2. A date after January 2026.
3. `delivery_from` later than `delivery_to`.
4. An unknown market profile.

Expected:

- Each invalid request returns `422`.
- Response explains what is invalid.
- Backend remains healthy after each request.

| Result | Notes/evidence |
|---|---|
|  |  |

---

## Data and analytical correctness

### TC-026 — Resolution explanation

Expected:

- Interface explains that actuals are derived from two half-hour periods.
- The comparison is presented at hourly resolution.
- Units are MW.

| Result | Notes/evidence |
|---|---|
|  |  |

### TC-027 — Error definition

Expected:

- Error is defined as `forecast - actual`.
- Positive bias is explained as over-forecasting.
- Negative bias is understood as under-forecasting.

| Result | Notes/evidence |
|---|---|
|  |  |

### TC-028 — No future-data leakage

**EPEX expectation:**

- Cutoff is 09:20 D−1.
- The latest eligible publication is 07:30 D−1.
- The 09:30 publication is not used.

**N2EX expectation:**

- Cutoff is 09:50 D−1.
- The latest eligible publication is 09:30 D−1.

Use the API response in Developer Tools → Network to inspect each point’s
`decision_cutoff` and `forecast_publish_time`.

| Result | Notes/evidence |
|---|---|
|  |  |

### TC-029 — Data-quality coverage

Expected for the full January EPEX analysis:

- 744 expected hours.
- 744 complete pairs.
- Zero missing forecasts.
- Zero missing actuals.
- No data-quality warnings.

| Result | Notes/evidence |
|---|---|
|  |  |

---

## Final acceptance record

| Area | Status | Notes |
|---|---|---|
| Automated backend checks |  |  |
| Automated frontend checks |  |  |
| Initial dashboard load |  |  |
| EPEX reference calculations |  |  |
| N2EX reference calculations |  |  |
| Date filters |  |  |
| Market-profile filters |  |  |
| Charts and tooltips |  |  |
| Error and recovery flow |  |  |
| Mobile layout |  |  |
| Tablet layout |  |  |
| Desktop layout |  |  |
| Keyboard accessibility |  |  |
| Console and network checks |  |  |
| API documentation |  |  |
| No-future-leakage verification |  |  |

## Release decision

```text
Overall result: PASS / FAIL / BLOCKED

Critical failures:

Non-critical observations:

Approved for deployment by:

Approval date:
```

The application should not proceed to deployment while any critical test is failing.
