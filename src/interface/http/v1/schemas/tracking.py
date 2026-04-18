"""Pydantic-схемы tracking/internal use-cases."""

from __future__ import annotations

from pydantic import BaseModel, Field


class MoneySchema(BaseModel):
    amount: float = Field(ge=0)
    currency: str = Field(min_length=3, max_length=3)


class TrackClickRequest(BaseModel):
    anonymous_id: str | None = None
    parent_id: str | None = None
    source_url: str | None = None


class TrackClickResponse(BaseModel):
    accepted: bool


class ResolveDiscountRequest(BaseModel):
    course_id: str
    referral_token: str | None = None
    channel: str | None = None
    parent_id: str | None = None


class ResolveDiscountResponse(BaseModel):
    valid: bool
    token: str | None = None
    channel: str
    campaign: str | None = None
    discount_type: str
    discount_value: float = Field(ge=0)
    discount: MoneySchema


class RecordRequestedConversionRequest(BaseModel):
    access_grant_id: str
    course_id: str
    student_id: str
    parent_id: str | None = None
    token: str | None = None
    channel: str
    discount: MoneySchema | None = None


class RecordPaidConversionRequest(BaseModel):
    access_grant_id: str
    paid_amount: MoneySchema
    approved_by_admin_id: str | None = None


class ConversionResponse(BaseModel):
    accepted: bool
