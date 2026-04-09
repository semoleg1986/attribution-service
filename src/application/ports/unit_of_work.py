"""Порт unit-of-work."""

from __future__ import annotations

from typing import Protocol

from src.application.ports.repositories import RepositoryProvider


class UnitOfWork(Protocol):
    """Контракт transactional boundary."""

    @property
    def repositories(self) -> RepositoryProvider:
        """Набор репозиториев в рамках одной операции."""

    def commit(self) -> None:
        """Зафиксировать изменения."""

    def rollback(self) -> None:
        """Откатить изменения."""
