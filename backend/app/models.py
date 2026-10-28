from datetime import date, datetime, time
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class MarketProfileName(StrEnum):
    EPEX_HOURLY = "epex_hourly"
    N2EX_HOURLY = "n2ex_hourly"


class MarketProfile(BaseModel):
    name: MarketProfileName
    label: str
    cutoff_local_time: time
    timezone: str = "Europe/London"
    product_resolution_minutes: int = 60
    description: str


MARKET_PROFILES: dict[MarketProfileName, MarketProfile] = {
    MarketProfileName.EPEX_HOURLY: MarketProfile(
        name=MarketProfileName.EPEX_HOURLY,
        label="EPEX hourly day-ahead",
        cutoff_local_time=time(9, 20),
        description="Orders close at 09:20 London time on the day before delivery.",
    ),
    MarketProfileName.N2EX_HOURLY: MarketProfile(
        name=MarketProfileName.N2EX_HOURLY,
        label="N2EX hourly day-ahead",
        cutoff_local_time=time(9, 50),
        description="Orders close at 09:50 London time on the day before delivery.",
    ),
}


class ActualRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    dataset: str
    publish_time: datetime = Field(alias="publishTime")
    start_time: datetime = Field(alias="startTime")
    settlement_date: date = Field(alias="settlementDate")
    settlement_period: int = Field(alias="settlementPeriod")
    fuel_type: str = Field(alias="fuelType")
    generation: int | None


class ForecastRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    dataset: str
    publish_time: datetime = Field(alias="publishTime")
    start_time: datetime = Field(alias="startTime")
    generation: int | None


class AnalysisPoint(BaseModel):
    delivery_time: datetime
    decision_cutoff: datetime
    forecast_publish_time: datetime | None
    forecast_mw: int | None
    actual_mw: float | None
    error_mw: float | None
    absolute_error_mw: float | None
    status: str


class MetricSummary(BaseModel):
    observations: int
    mae_mw: float | None
    rmse_mw: float | None
    bias_mw: float | None
    wape_percent: float | None
    over_forecast_percent: float | None
    under_forecast_percent: float | None


class CoverageSummary(BaseModel):
    expected_hours: int
    complete_pairs: int
    missing_forecasts: int
    missing_actuals: int


class DataQualitySummary(BaseModel):
    actual_source_records: int
    forecast_source_records: int
    duplicate_actual_records: int
    duplicate_forecast_records: int
    warnings: list[str]


class AnalysisResponse(BaseModel):
    delivery_from: date
    delivery_to: date
    market_profile: MarketProfile
    units: str = "MW"
    error_definition: str = "forecast - actual"
    actual_resolution: str = "Mean of two consecutive 30-minute FUELHH values"
    metrics: MetricSummary
    coverage: CoverageSummary
    data_quality: DataQualitySummary
    points: list[AnalysisPoint]
