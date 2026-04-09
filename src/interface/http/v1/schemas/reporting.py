"""Pydantic-схемы отчетности."""

from __future__ import annotations

from pydantic import BaseModel

from src.interface.http.v1.schemas.tracking import MoneySchema


class ChannelReportItemResponse(BaseModel):
    channel: str
    clicks: int
    requested: int
    paid: int
    paid_revenue: MoneySchema


class ChannelReportResponse(BaseModel):
    items: list[ChannelReportItemResponse]
