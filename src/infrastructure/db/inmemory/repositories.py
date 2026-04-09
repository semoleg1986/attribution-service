"""In-memory репозитории attribution-service."""

from __future__ import annotations

from datetime import date

from src.domain.conversions.conversion.entity import AttributionConversion
from src.domain.shared.statuses import AttributionChannel, TokenStatus
from src.domain.tokens.referral_token.entity import ReferralToken
from src.domain.visits.visit.entity import AttributionVisit


class InMemoryReferralTokenRepository:
    """In-memory реализация репозитория referral tokens."""

    def __init__(self) -> None:
        self._items: dict[str, ReferralToken] = {}

    def get(self, token: str) -> ReferralToken | None:
        return self._items.get(token)

    def save(self, referral_token: ReferralToken) -> None:
        self._items[referral_token.token] = referral_token

    def list(
        self,
        *,
        channel: AttributionChannel | None = None,
        status: TokenStatus | None = None,
    ) -> list[ReferralToken]:
        items = list(self._items.values())
        if channel is not None:
            items = [item for item in items if item.channel == channel]
        if status is not None:
            items = [item for item in items if item.status == status]
        return sorted(items, key=lambda item: item.meta.created_at)


class InMemoryAttributionVisitRepository:
    """In-memory реализация репозитория фактов перехода."""

    def __init__(self) -> None:
        self._items: list[AttributionVisit] = []

    def add(self, visit: AttributionVisit) -> None:
        self._items.append(visit)

    def count(
        self,
        *,
        channel: AttributionChannel | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> int:
        count = 0
        for item in self._items:
            if channel is not None and item.channel != channel:
                continue
            if date_from is not None and item.clicked_at.date() < date_from:
                continue
            if date_to is not None and item.clicked_at.date() > date_to:
                continue
            count += 1
        return count


class InMemoryAttributionConversionRepository:
    """In-memory реализация репозитория конверсий."""

    def __init__(self) -> None:
        self._items: dict[str, AttributionConversion] = {}

    def get(self, access_grant_id: str) -> AttributionConversion | None:
        return self._items.get(access_grant_id)

    def save(self, conversion: AttributionConversion) -> None:
        self._items[conversion.access_grant_id] = conversion

    def list(
        self,
        *,
        channel: AttributionChannel | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[AttributionConversion]:
        items = list(self._items.values())
        if channel is not None:
            items = [item for item in items if item.channel == channel]
        if date_from is not None:
            items = [item for item in items if item.meta.created_at.date() >= date_from]
        if date_to is not None:
            items = [item for item in items if item.meta.created_at.date() <= date_to]
        return sorted(items, key=lambda item: item.meta.created_at)
