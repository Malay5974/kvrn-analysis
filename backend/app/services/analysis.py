import asyncio
from datetime import UTC, date, datetime, time, timedelta

from app.clients.elexon import ElexonClient
from app.domain.analysis import analyse, decision_cutoff
from app.models import AnalysisResponse, MarketProfile


class AnalysisService:
    def __init__(self, client: ElexonClient) -> None:
        self._client = client

    async def run(
        self, delivery_from: date, delivery_to: date, profile: MarketProfile
    ) -> AnalysisResponse:
        # WINDFOR publishes a rolling D-to-D+2 horizon. Three days of lookback
        # safely include every vintage eligible for the first delivery date.
        publish_from = datetime.combine(
            delivery_from - timedelta(days=3), time.min, tzinfo=UTC
        )
        last_cutoff = decision_cutoff(delivery_to, profile)
        publish_to = last_cutoff + timedelta(minutes=1)

        actuals, forecasts = await asyncio.gather(
            self._client.fetch_actuals(delivery_from, delivery_to),
            self._client.fetch_forecasts(publish_from, publish_to),
        )
        points, metrics, coverage, quality = analyse(
            actuals, forecasts, delivery_from, delivery_to, profile
        )
        return AnalysisResponse(
            delivery_from=delivery_from,
            delivery_to=delivery_to,
            market_profile=profile,
            metrics=metrics,
            coverage=coverage,
            data_quality=quality,
            points=points,
        )
