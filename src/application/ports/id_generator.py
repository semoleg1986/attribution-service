"""Порт генерации идентификаторов."""

from __future__ import annotations

from typing import Protocol


class IdGenerator(Protocol):
    """Контракт генератора id."""

    def new(self) -> str:
        """Вернуть новый id."""
