from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class EntityMeta:
    """
    Метаданные сущности/агрегата атрибуции.

    :param version: Версия для optimistic concurrency.
    :type version: int
    :param created_at: Время создания.
    :type created_at: datetime
    :param created_by: Идентификатор актора-создателя.
    :type created_by: str
    :param updated_at: Время последнего изменения.
    :type updated_at: datetime
    :param updated_by: Идентификатор актора последнего изменения.
    :type updated_by: str
    """

    version: int
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
    archived_at: datetime | None = None
    archived_by: str | None = None

    @classmethod
    def create(cls, at: datetime, actor_id: str) -> "EntityMeta":
        """Создать начальные метаданные."""
        return cls(
            version=1,
            created_at=at,
            created_by=actor_id,
            updated_at=at,
            updated_by=actor_id,
        )

    def touch(self, at: datetime, actor_id: str) -> None:
        """Обновить версию и audit-поля изменения."""
        self.version += 1
        self.updated_at = at
        self.updated_by = actor_id

    def mark_archived(self, at: datetime, actor_id: str) -> None:
        """Зафиксировать архивирование записи."""
        self.archived_at = at
        self.archived_by = actor_id
        self.touch(at=at, actor_id=actor_id)
