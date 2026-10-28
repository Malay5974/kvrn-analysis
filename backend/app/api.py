from collections.abc import AsyncIterator
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.clients.elexon import ElexonClient, ElexonError
from app.config import Settings, get_settings
from app.domain.analysis import DataConflictError
from app.models import (
    MARKET_PROFILES,
    AnalysisResponse,
    MarketProfile,
    MarketProfileName,
)
from app.services.analysis import AnalysisService

router = APIRouter()


async def get_elexon_client(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AsyncIterator[ElexonClient]:
    client = ElexonClient(
        base_url=settings.elexon_base_url,
        timeout_seconds=settings.elexon_timeout_seconds,
        max_attempts=settings.elexon_max_attempts,
    )
    try:
        yield client
    finally:
        await client.aclose()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/api/v1/market-profiles", response_model=list[MarketProfile])
async def market_profiles() -> list[MarketProfile]:
    return list(MARKET_PROFILES.values())


@router.get("/api/v1/analysis", response_model=AnalysisResponse)
async def analysis(
    client: Annotated[ElexonClient, Depends(get_elexon_client)],
    delivery_from: Annotated[date, Query()] = date(2026, 1, 1),
    delivery_to: Annotated[date, Query()] = date(2026, 1, 31),
    market_profile: Annotated[MarketProfileName, Query()] = MarketProfileName.EPEX_HOURLY,
) -> AnalysisResponse:
    if delivery_from > delivery_to:
        raise HTTPException(status_code=422, detail="delivery_from must not be after delivery_to")
    if delivery_from < date(2026, 1, 1) or delivery_to > date(2026, 1, 31):
        raise HTTPException(
            status_code=422,
            detail="This pilot is limited to delivery dates in January 2026",
        )

    try:
        return await AnalysisService(client).run(
            delivery_from, delivery_to, MARKET_PROFILES[market_profile]
        )
    except ElexonError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except DataConflictError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
