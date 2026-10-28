# Wind Decision Intelligence

A full-stack pilot for evaluating the wind-generation forecast that was available when a
UK day-ahead electricity purchasing decision had to be made. The analysis uses Elexon
`WINDFOR` forecasts and `FUELHH` wind-generation actuals for January 2026.

## Current status

The analytical backend and interactive React dashboard are implemented. The dashboard includes
market and date controls, decision context, accuracy metrics, forecast-versus-actual generation,
daily bias, a buyer-facing interpretation, loading/error states, and data-quality coverage.

## Live application

- Dashboard: https://kvrn-analysis-web.vercel.app
- API documentation: https://kvrn-analysis-api.vercel.app/docs
- API health check: https://kvrn-analysis-api.vercel.app/health
- Source repository: https://github.com/Malay5974/kvrn-analysis

## Decision model

The default market profile is the EPEX hourly day-ahead auction. For each delivery day, the
application selects the latest forecast whose `publishTime` is at or before 09:20 London time
on the previous day. This prevents future-data leakage.

Because `WINDFOR` targets are hourly while `FUELHH` actuals are half-hourly, two consecutive
actual values are averaged before comparison. Errors use `forecast - actual`, so a positive
bias means over-forecasting.

## Project structure

- `backend/app/clients`: Elexon HTTP integration and bounded retries
- `backend/app/domain`: pure cutoff, alignment, selection, and metric logic
- `backend/app/services`: orchestration of data retrieval and analysis
- `backend/tests`: decision-rule, data-quality, metric, and retry tests
- `frontend/src`: React dashboard, typed API integration, and analysis helpers
- `frontend/src/components`: lazy-loaded charts and reusable dashboard components
- `docker-compose.yml`: local full-stack runtime
- `TESTING.md`: automated and manual end-to-end test guidance
- `DEMO_SCRIPT.md`: timed customer demo and technical handover script
- `SUBMISSION_CHECKLIST.md`: final assessment submission checklist

## Run with Docker

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- API documentation: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Run the backend locally

Python 3.12 or 3.13 is recommended.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn app.main:app --reload
```

Tests and lint:

```bash
pytest
ruff check .
```

## Run the frontend locally

```bash
cd frontend
npm install
npm run dev
```

Frontend checks:

```bash
npm run test
npm run lint
npm run build
```

## API example

```text
GET /api/v1/analysis?delivery_from=2026-01-01&delivery_to=2026-01-31&market_profile=epex_hourly
```

## Deployment

The frontend and backend are deployed as separate Vercel projects. The frontend build receives
the backend URL through `VITE_API_BASE_URL`, while the backend restricts browser access through
the `CORS_ORIGINS` environment setting. The framework configuration is recorded in each
application's `vercel.json`.

## Data source and attribution

Contains BMRS data © Elexon Limited copyright and database right.

## AI-tool disclosure

AI tools were used to assist with domain research, architecture, implementation, and review.
All decision rules, calculations, and tests are intended to be independently reviewable.
