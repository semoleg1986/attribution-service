"""Query DTO reporting use-cases."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True)
class GetChannelReportQuery:
    date_from: date
    date_to: date
    actor_id: str
    actor_roles: list[str]


@dataclass(frozen=True, slots=True)
class GetCampaignReportQuery:
    date_from: date
    date_to: date
    actor_id: str
    actor_roles: list[str]
    channel: str | None = None
    limit: int = 50
    offset: int = 0
