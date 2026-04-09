"""Query DTO tokens use-cases."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ListReferralTokensQuery:
    actor_id: str
    actor_roles: list[str]
    channel: str | None = None
    status: str | None = None
