from __future__ import annotations

from datetime import date
from typing import Protocol

from src.domain.shared.statuses import AttributionChannel

from .entity import AttributionVisit


class AttributionVisitRepository(Protocol):
    """Репозиторий фактов переходов AttributionVisit."""

    def add(self, visit: AttributionVisit) -> None:
        """Добавить факт перехода."""

    def count(
        self,
        *,
        channel: AttributionChannel | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> int:
        """Посчитать клики по фильтрам."""
