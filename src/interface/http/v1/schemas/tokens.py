"""Pydantic-схемы для token use-cases."""

from __future__ import annotations

import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

_TRACKING_PART = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


def _ensure_tz_aware(value: datetime | None, field_name: str) -> datetime | None:
    """Проверяет, что datetime содержит timezone offset."""
    if value is None:
        return None
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} должен содержать timezone offset")
    return value


class CreateReferralTokenRequest(BaseModel):
    channel: str
    campaign: str | None = None
    source: str | None = None
    medium: str | None = None
    course_id: str | None = None
    discount_type: str
    discount_value: float = Field(ge=0)
    expires_at: datetime | None = None
    course_starts_at: datetime | None = None

    @field_validator("expires_at", "course_starts_at", mode="after")
    @classmethod
    def ensure_datetime_has_timezone(
        cls, value: datetime | None, info: object
    ) -> datetime | None:
        field_name = getattr(info, "field_name", "datetime")
        return _ensure_tz_aware(value, field_name)

    @field_validator("campaign", "source", "medium", mode="after")
    @classmethod
    def ensure_tracking_field_format(
        cls, value: str | None, info: object
    ) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        field_name = getattr(info, "field_name", "tracking_field")
        if not normalized:
            return None
        if not _TRACKING_PART.fullmatch(normalized):
            raise ValueError(
                f"{field_name} должен содержать только lowercase latin, digits, '_' или '-'"
            )
        return normalized


class ReferralTokenResponse(BaseModel):
    token: str
    status: str
    channel: str
    campaign: str | None = None
    source: str | None = None
    medium: str | None = None
    course_id: str | None = None
    discount_type: str
    discount_value: float
    expires_at: datetime


class ReferralTokenListResponse(BaseModel):
    items: list[ReferralTokenResponse]
