"""Pydantic-схемы для token use-cases."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


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


class ReferralTokenResponse(BaseModel):
    token: str
    status: str
    channel: str
    campaign: str | None = None
    course_id: str | None = None
    discount_type: str
    discount_value: float
    expires_at: datetime


class ReferralTokenListResponse(BaseModel):
    items: list[ReferralTokenResponse]
