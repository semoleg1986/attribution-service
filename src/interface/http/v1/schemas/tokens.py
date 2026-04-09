"""Pydantic-схемы для token use-cases."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class CreateReferralTokenRequest(BaseModel):
    channel: str
    campaign: str | None = None
    course_id: str | None = None
    discount_type: str
    discount_value: float = Field(ge=0)
    expires_at: datetime | None = None
    course_starts_at: datetime | None = None


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
