"""Command DTO tokens use-cases."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class CreateReferralTokenCommand:
    channel: str
    discount_type: str
    discount_value: float
    course_id: str | None
    campaign: str | None
    source: str | None
    medium: str | None
    expires_at: datetime | None
    course_starts_at: datetime | None
    actor_id: str
    actor_roles: list[str]


@dataclass(frozen=True, slots=True)
class DisableReferralTokenCommand:
    token: str
    actor_id: str
    actor_roles: list[str]
