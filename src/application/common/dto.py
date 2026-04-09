"""DTO application-слоя attribution-service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class MoneyResult:
    amount: float
    currency: str


@dataclass(frozen=True, slots=True)
class ReferralTokenResult:
    token: str
    status: str
    channel: str
    campaign: str | None
    course_id: str | None
    discount_type: str
    discount_value: float
    expires_at: datetime


@dataclass(frozen=True, slots=True)
class TrackClickResult:
    accepted: bool


@dataclass(frozen=True, slots=True)
class ResolveDiscountResult:
    valid: bool
    token: str | None
    channel: str
    campaign: str | None
    discount: MoneyResult


@dataclass(frozen=True, slots=True)
class ConversionResult:
    accepted: bool


@dataclass(frozen=True, slots=True)
class ChannelReportItemResult:
    channel: str
    clicks: int
    requested: int
    paid: int
    paid_revenue: MoneyResult
