"""Системные часы."""

from __future__ import annotations

from datetime import UTC, datetime


class SystemClock:
    """Возвращает текущее UTC время."""

    def now(self) -> datetime:
        return datetime.now(UTC)
