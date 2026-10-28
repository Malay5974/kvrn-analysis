from datetime import UTC, date, datetime

from fastapi.testclient import TestClient

from app.api import get_elexon_client
from app.main import app
from app.models import ActualRecord, ForecastRecord


class FakeElexonClient:
    async def fetch_actuals(self, start: date, end: date) -> list[ActualRecord]:
        return [
            ActualRecord(
                dataset="FUELHH",
                publishTime=datetime(2026, 1, 2, 0, 30, tzinfo=UTC),
                startTime=datetime(2026, 1, 2, 0, 0, tzinfo=UTC),
                settlementDate=date(2026, 1, 2),
                settlementPeriod=1,
                fuelType="WIND",
                generation=100,
            ),
            ActualRecord(
                dataset="FUELHH",
                publishTime=datetime(2026, 1, 2, 1, 0, tzinfo=UTC),
                startTime=datetime(2026, 1, 2, 0, 30, tzinfo=UTC),
                settlementDate=date(2026, 1, 2),
                settlementPeriod=2,
                fuelType="WIND",
                generation=120,
            ),
        ]

    async def fetch_forecasts(
        self, publish_from: datetime, publish_to: datetime
    ) -> list[ForecastRecord]:
        return [
            ForecastRecord(
                dataset="WINDFOR",
                publishTime=datetime(2026, 1, 1, 7, 30, tzinfo=UTC),
                startTime=datetime(2026, 1, 2, 0, 0, tzinfo=UTC),
                generation=130,
            )
        ]

    async def aclose(self) -> None:
        return None


def test_analysis_endpoint_exposes_decision_context_and_coverage() -> None:
    app.dependency_overrides[get_elexon_client] = lambda: FakeElexonClient()
    try:
        with TestClient(app) as client:
            response = client.get(
                "/api/v1/analysis",
                params={"delivery_from": "2026-01-02", "delivery_to": "2026-01-02"},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["market_profile"]["name"] == "epex_hourly"
    assert payload["metrics"]["observations"] == 1
    assert payload["coverage"] == {
        "expected_hours": 24,
        "complete_pairs": 1,
        "missing_forecasts": 23,
        "missing_actuals": 0,
    }
    assert payload["points"][0]["decision_cutoff"] == "2026-01-01T09:20:00Z"


def test_analysis_endpoint_rejects_dates_outside_pilot_scope() -> None:
    with TestClient(app) as client:
        response = client.get(
            "/api/v1/analysis",
            params={"delivery_from": "2025-12-31", "delivery_to": "2026-01-02"},
        )

    assert response.status_code == 422
    assert response.json()["detail"] == "This pilot is limited to delivery dates in January 2026"


def test_local_frontend_origin_is_allowed_by_cors() -> None:
    with TestClient(app) as client:
        response = client.options(
            "/api/v1/analysis",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"
