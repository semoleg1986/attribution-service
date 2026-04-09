"""Порт часов."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol


class Clock(Protocol):
    """Контракт источника текущего времени."""

    def now(self) -> datetime:
        """Вернуть текущее время."""
