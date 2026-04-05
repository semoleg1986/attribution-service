from __future__ import annotations

from typing import Protocol

from .entity import AttributionVisit


class AttributionVisitRepository(Protocol):
    """Репозиторий фактов переходов AttributionVisit."""

    def add(self, visit: AttributionVisit) -> None:
        """Добавить факт перехода."""
