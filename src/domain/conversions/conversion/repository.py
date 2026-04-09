from __future__ import annotations

from datetime import date
from typing import Protocol

from src.domain.shared.statuses import AttributionChannel

from .entity import AttributionConversion


class AttributionConversionRepository(Protocol):
    """Репозиторий агрегата AttributionConversion."""

    def get(self, access_grant_id: str) -> AttributionConversion | None:
        """Получить конверсию по id access grant."""

    def save(self, conversion: AttributionConversion) -> None:
        """Сохранить агрегат AttributionConversion."""

    def list(
        self,
        *,
        channel: AttributionChannel | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> list[AttributionConversion]:
        """Вернуть конверсии по фильтрам."""
