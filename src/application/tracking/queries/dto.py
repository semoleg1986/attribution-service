"""Query DTO discount-resolution use-case."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ResolveDiscountQuery:
    course_id: str
    referral_token: str | None
    channel: str | None
    parent_id: str | None
    actor_id: str
    actor_roles: list[str]
