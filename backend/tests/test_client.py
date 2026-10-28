import httpx
import pytest

from app.clients.elexon import ElexonClient, ElexonError


@pytest.mark.asyncio
async def test_client_retries_rate_limit_then_succeeds() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            return httpx.Response(429, request=request)
        return httpx.Response(200, json=[], request=request)

    async with ElexonClient(
        "https://example.test", max_attempts=5, transport=httpx.MockTransport(handler)
    ) as client:
        result = await client.fetch_forecasts(
            __import__("datetime").datetime.now(__import__("datetime").UTC),
            __import__("datetime").datetime.now(__import__("datetime").UTC),
        )

    assert result == []
    assert attempts == 3


@pytest.mark.asyncio
async def test_client_does_not_retry_bad_request() -> None:
    attempts = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(400, request=request)

    async with ElexonClient(
        "https://example.test", max_attempts=5, transport=httpx.MockTransport(handler)
    ) as client:
        with pytest.raises(ElexonError, match="status 400"):
            await client.fetch_actuals(
                __import__("datetime").date(2026, 1, 1),
                __import__("datetime").date(2026, 1, 2),
            )

    assert attempts == 1
