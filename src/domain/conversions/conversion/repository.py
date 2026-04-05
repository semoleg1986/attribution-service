from __future__ import annotations

from typing import Protocol

from .entity import AttributionConversion


class AttributionConversionRepository(Protocol):
    """Репозиторий агрегата AttributionConversion."""

    def get(self, access_grant_id: str) -> AttributionConversion | None:
        """Получить конверсию по id access grant."""

    def save(self, conversion: AttributionConversion) -> None:
        """Сохранить агрегат AttributionConversion."""
