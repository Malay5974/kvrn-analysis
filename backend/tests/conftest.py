from datetime import UTC, date, datetime

from app.models import ActualRecord, ForecastRecord


def actual(start_hour: int, start_minute: int, generation: int | None) -> ActualRecord:
    start = datetime(2026, 1, 2, start_hour, start_minute, tzinfo=UTC)
    return ActualRecord(
        dataset="FUELHH",
        publishTime=start.replace(minute=start_minute) if start_minute else start,
        startTime=start,
        settlementDate=date(2026, 1, 2),
        settlementPeriod=start_hour * 2 + (2 if start_minute else 1),
        fuelType="WIND",
        generation=generation,
    )


def forecast(
    target_hour: int, publish_hour: int, publish_minute: int, generation: int | None
) -> ForecastRecord:
    return ForecastRecord(
        dataset="WINDFOR",
        publishTime=datetime(2026, 1, 1, publish_hour, publish_minute, tzinfo=UTC),
        startTime=datetime(2026, 1, 2, target_hour, 0, tzinfo=UTC),
        generation=generation,
    )
