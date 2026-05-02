"""ORM-модели attribution-service."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.sqlalchemy.base import Base


class ReferralTokenModel(Base):
    """ORM-модель реферального токена."""

    __tablename__ = "referral_tokens"

    token: Mapped[str] = mapped_column(String(64), primary_key=True)
    channel: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    discount_type: Mapped[str] = mapped_column(String(16), nullable=False)
    discount_value: Mapped[float] = mapped_column(Float, nullable=False)
    course_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    campaign: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    medium: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    policy_locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_by: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_by: Mapped[str] = mapped_column(String(64), nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    archived_by: Mapped[str | None] = mapped_column(String(64), nullable=True)


class AttributionVisitModel(Base):
    """ORM-модель факта перехода."""

    __tablename__ = "attribution_visits"

    visit_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    token: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    clicked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    parent_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    anonymous_id: Mapped[str | None] = mapped_column(
        String(128), nullable=True, index=True
    )
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_by: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_by: Mapped[str] = mapped_column(String(64), nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    archived_by: Mapped[str | None] = mapped_column(String(64), nullable=True)


class AttributionConversionModel(Base):
    """ORM-модель конверсии воронки оплаты."""

    __tablename__ = "attribution_conversions"

    access_grant_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    course_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    student_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    token: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    parent_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    requested_recorded: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    paid_recorded: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    requested_discount_amount: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    requested_discount_currency: Mapped[str | None] = mapped_column(
        String(3), nullable=True
    )
    paid_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    paid_currency: Mapped[str | None] = mapped_column(String(3), nullable=True)

    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_by: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_by: Mapped[str] = mapped_column(String(64), nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    archived_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
