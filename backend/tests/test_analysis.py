from datetime import UTC, date, datetime

import pytest

from app.domain.analysis import DataConflictError, analyse, decision_cutoff
from app.models import MARKET_PROFILES, MarketProfileName
from tests.conftest import actual, forecast


def test_decision_cutoff_is_previous_day_in_utc_for_january() -> None:
    profile = MARKET_PROFILES[MarketProfileName.EPEX_HOURLY]

    result = decision_cutoff(date(2026, 1, 2), profile)

    assert result == datetime(2026, 1, 1, 9, 20, tzinfo=UTC)


def test_selects_latest_forecast_available_before_cutoff() -> None:
    profile = MARKET_PROFILES[MarketProfileName.EPEX_HOURLY]
    actuals = [actual(0, 0, 100), actual(0, 30, 120)]
    forecasts = [
        forecast(0, 7, 30, 130),
        forecast(0, 9, 30, 90),
    ]

    points, metrics, coverage, _ = analyse(
        actuals, forecasts, date(2026, 1, 2), date(2026, 1, 2), profile
    )

    assert points[0].forecast_publish_time == datetime(2026, 1, 1, 7, 30, tzinfo=UTC)
    assert points[0].forecast_mw == 130
    assert points[0].actual_mw == 110
    assert points[0].error_mw == 20
    assert metrics.observations == 1
    assert coverage.missing_forecasts == 23


def test_hour_is_incomplete_when_one_actual_half_hour_is_missing() -> None:
    profile = MARKET_PROFILES[MarketProfileName.EPEX_HOURLY]

    points, metrics, coverage, _ = analyse(
        [actual(0, 0, 100)],
        [forecast(0, 7, 30, 130)],
        date(2026, 1, 2),
        date(2026, 1, 2),
        profile,
    )

    assert points[0].status == "missing_actual"
    assert metrics.observations == 0
    assert coverage.missing_actuals == 1


def test_conflicting_duplicate_actuals_fail_loudly() -> None:
    profile = MARKET_PROFILES[MarketProfileName.EPEX_HOURLY]

    with pytest.raises(DataConflictError, match="Conflicting actual generation"):
        analyse(
            [actual(0, 0, 100), actual(0, 0, 101)],
            [forecast(0, 7, 30, 130)],
            date(2026, 1, 2),
            date(2026, 1, 2),
            profile,
        )


def test_metrics_use_forecast_minus_actual_sign_convention() -> None:
    profile = MARKET_PROFILES[MarketProfileName.EPEX_HOURLY]
    actuals = [
        actual(0, 0, 100),
        actual(0, 30, 100),
        actual(1, 0, 200),
        actual(1, 30, 200),
    ]
    forecasts = [forecast(0, 7, 30, 110), forecast(1, 7, 30, 180)]

    _, metrics, _, _ = analyse(
        actuals, forecasts, date(2026, 1, 2), date(2026, 1, 2), profile
    )

    assert metrics.observations == 2
    assert metrics.mae_mw == 15
    assert metrics.bias_mw == -5
    assert metrics.wape_percent == 10
    assert metrics.over_forecast_percent == 50
    assert metrics.under_forecast_percent == 50
