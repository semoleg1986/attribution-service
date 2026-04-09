"""In-memory unit-of-work attribution-service."""

from __future__ import annotations

from dataclasses import dataclass

from src.application.ports.repositories import RepositoryProvider


@dataclass(frozen=True, slots=True)
class InMemoryRepositoryProvider(RepositoryProvider):
    """Конкретный provider для in-memory режима."""


class InMemoryUnitOfWork:
    """No-op UoW для in-memory хранилища."""

    def __init__(self, repositories: InMemoryRepositoryProvider) -> None:
        self._repositories = repositories

    @property
    def repositories(self) -> InMemoryRepositoryProvider:
        return self._repositories

    def commit(self) -> None:
        return None

    def rollback(self) -> None:
        return None
