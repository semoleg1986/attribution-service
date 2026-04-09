"""Генератор идентификаторов."""

from __future__ import annotations

from uuid import uuid4


class UuidGenerator:
    """Генерирует случайные UUID v4."""

    def new(self) -> str:
        return str(uuid4())
