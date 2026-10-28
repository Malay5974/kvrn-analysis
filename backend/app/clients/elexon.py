import asyncio
from datetime import date, datetime
from typing import Any

import httpx

from app.models import ActualRecord, ForecastRecord


class ElexonError(RuntimeError):
    """Raised when the Elexon service cannot provide a valid response."""


class ElexonClient:
    def __init__(
        self,
        base_url: str,
        timeout_seconds: float = 30.0,
        max_attempts: int = 5,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._max_attempts = max_attempts
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            timeout=timeout_seconds,
            transport=transport,
            headers={"Accept": "application/json", "User-Agent": "gridbricks-challenge/0.1"},
        )

    async def __aenter__(self) -> "ElexonClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    async def fetch_actuals(self, start: date, end: date) -> list[ActualRecord]:
        payload = await self._get(
            "/datasets/FUELHH/stream",
            params={
                "settlementDateFrom": start.isoformat(),
                "settlementDateTo": end.isoformat(),
                "fuelType": "WIND",
            },
        )
        return [ActualRecord.model_validate(item) for item in payload]

    async def fetch_forecasts(
        self, publish_from: datetime, publish_to: datetime
    ) -> list[ForecastRecord]:
        payload = await self._get(
            "/datasets/WINDFOR/stream",
            params={
                "publishDateTimeFrom": publish_from.isoformat().replace("+00:00", "Z"),
                "publishDateTimeTo": publish_to.isoformat().replace("+00:00", "Z"),
            },
        )
        return [ForecastRecord.model_validate(item) for item in payload]

    async def _get(self, path: str, params: dict[str, str]) -> list[dict[str, Any]]:
        last_error: Exception | None = None
        for attempt in range(1, self._max_attempts + 1):
            try:
                response = await self._client.get(path, params=params)
                if response.status_code != 429:
                    response.raise_for_status()
                    payload = response.json()
                    if not isinstance(payload, list):
                        raise ElexonError("Elexon returned a non-list payload")
                    return payload
                last_error = ElexonError("Elexon rate limit reached")
            except (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError) as exc:
                last_error = exc
                if isinstance(exc, httpx.HTTPStatusError) and exc.response.status_code < 500:
                    raise ElexonError(
                        f"Elexon request rejected with status {exc.response.status_code}"
                    ) from exc

            if attempt < self._max_attempts:
                await asyncio.sleep(0.25 * (2 ** (attempt - 1)))

        raise ElexonError(
            f"Elexon request failed after {self._max_attempts} attempts"
        ) from last_error
