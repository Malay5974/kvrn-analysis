from collections import defaultdict
from datetime import UTC, date, datetime, time, timedelta
from math import sqrt
from zoneinfo import ZoneInfo

from app.models import (
    ActualRecord,
    AnalysisPoint,
    CoverageSummary,
    DataQualitySummary,
    ForecastRecord,
    MarketProfile,
    MetricSummary,
)


class DataConflictError(ValueError):
    """Raised when duplicate source rows disagree on generation."""


def decision_cutoff(delivery_day: date, profile: MarketProfile) -> datetime:
    local_zone = ZoneInfo(profile.timezone)
    local_cutoff = datetime.combine(
        delivery_day - timedelta(days=1), profile.cutoff_local_time, tzinfo=local_zone
    )
    return local_cutoff.astimezone(UTC)


def analyse(
    actuals: list[ActualRecord],
    forecasts: list[ForecastRecord],
    delivery_from: date,
    delivery_to: date,
    profile: MarketProfile,
) -> tuple[list[AnalysisPoint], MetricSummary, CoverageSummary, DataQualitySummary]:
    actual_by_time, duplicate_actuals = _deduplicate_actuals(actuals)
    forecast_by_target, duplicate_forecasts = _deduplicate_forecasts(forecasts)

    points: list[AnalysisPoint] = []
    current = datetime.combine(delivery_from, time.min, tzinfo=UTC)
    final = datetime.combine(delivery_to + timedelta(days=1), time.min, tzinfo=UTC)

    while current < final:
        cutoff = decision_cutoff(current.date(), profile)
        eligible = [
            record
            for record in forecast_by_target.get(current, [])
            if record.publish_time <= cutoff and record.generation is not None
        ]
        selected = max(eligible, key=lambda record: record.publish_time, default=None)
        first_half = actual_by_time.get(current)
        second_half = actual_by_time.get(current + timedelta(minutes=30))
        actual_mw = (
            (first_half + second_half) / 2
            if first_half is not None and second_half is not None
            else None
        )

        if selected is None:
            status = "missing_forecast"
        elif actual_mw is None:
            status = "missing_actual"
        else:
            status = "complete"

        error = (
            float(selected.generation) - actual_mw
            if selected is not None and selected.generation is not None and actual_mw is not None
            else None
        )
        points.append(
            AnalysisPoint(
                delivery_time=current,
                decision_cutoff=cutoff,
                forecast_publish_time=selected.publish_time if selected else None,
                forecast_mw=selected.generation if selected else None,
                actual_mw=actual_mw,
                error_mw=error,
                absolute_error_mw=abs(error) if error is not None else None,
                status=status,
            )
        )
        current += timedelta(hours=1)

    metrics = calculate_metrics(points)
    coverage = CoverageSummary(
        expected_hours=len(points),
        complete_pairs=metrics.observations,
        missing_forecasts=sum(point.status == "missing_forecast" for point in points),
        missing_actuals=sum(point.status == "missing_actual" for point in points),
    )
    warnings: list[str] = []
    if coverage.missing_forecasts:
        warnings.append(f"{coverage.missing_forecasts} hourly forecasts are unavailable")
    if coverage.missing_actuals:
        warnings.append(f"{coverage.missing_actuals} hourly actual values are incomplete")

    quality = DataQualitySummary(
        actual_source_records=len(actuals),
        forecast_source_records=len(forecasts),
        duplicate_actual_records=duplicate_actuals,
        duplicate_forecast_records=duplicate_forecasts,
        warnings=warnings,
    )
    return points, metrics, coverage, quality


def calculate_metrics(points: list[AnalysisPoint]) -> MetricSummary:
    complete = [point for point in points if point.status == "complete"]
    if not complete:
        return MetricSummary(
            observations=0,
            mae_mw=None,
            rmse_mw=None,
            bias_mw=None,
            wape_percent=None,
            over_forecast_percent=None,
            under_forecast_percent=None,
        )

    errors = [point.error_mw for point in complete if point.error_mw is not None]
    actuals = [point.actual_mw for point in complete if point.actual_mw is not None]
    count = len(errors)
    absolute_error_sum = sum(abs(error) for error in errors)
    actual_sum = sum(actuals)
    return MetricSummary(
        observations=count,
        mae_mw=absolute_error_sum / count,
        rmse_mw=sqrt(sum(error**2 for error in errors) / count),
        bias_mw=sum(errors) / count,
        wape_percent=(absolute_error_sum / actual_sum * 100) if actual_sum else None,
        over_forecast_percent=sum(error > 0 for error in errors) / count * 100,
        under_forecast_percent=sum(error < 0 for error in errors) / count * 100,
    )


def _deduplicate_actuals(actuals: list[ActualRecord]) -> tuple[dict[datetime, int | None], int]:
    result: dict[datetime, int | None] = {}
    duplicates = 0
    for record in actuals:
        if record.fuel_type != "WIND":
            continue
        if record.start_time in result:
            duplicates += 1
            if result[record.start_time] != record.generation:
                raise DataConflictError(
                    f"Conflicting actual generation at {record.start_time.isoformat()}"
                )
        result[record.start_time] = record.generation
    return result, duplicates


def _deduplicate_forecasts(
    forecasts: list[ForecastRecord],
) -> tuple[dict[datetime, list[ForecastRecord]], int]:
    unique: dict[tuple[datetime, datetime], ForecastRecord] = {}
    duplicates = 0
    for record in forecasts:
        key = (record.publish_time, record.start_time)
        if key in unique:
            duplicates += 1
            if unique[key].generation != record.generation:
                raise DataConflictError(
                    "Conflicting forecast generation for publication "
                    f"{record.publish_time.isoformat()} and target {record.start_time.isoformat()}"
                )
        unique[key] = record

    by_target: dict[datetime, list[ForecastRecord]] = defaultdict(list)
    for record in unique.values():
        by_target[record.start_time].append(record)
    return dict(by_target), duplicates
