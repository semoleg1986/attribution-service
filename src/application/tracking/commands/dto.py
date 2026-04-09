"""Command DTO tracking/conversion use-cases."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TrackVisitCommand:
    token: str
    anonymous_id: str | None
    parent_id: str | None
    source_url: str | None


@dataclass(frozen=True, slots=True)
class RecordRequestedConversionCommand:
    access_grant_id: str
    course_id: str
    student_id: str
    parent_id: str | None
    token: str | None
    channel: str
    discount_amount: float | None
    discount_currency: str | None
    actor_id: str
    actor_roles: list[str]


@dataclass(frozen=True, slots=True)
class RecordPaidConversionCommand:
    access_grant_id: str
    paid_amount: float
    currency: str
    approved_by_admin_id: str | None
    actor_id: str
    actor_roles: list[str]
