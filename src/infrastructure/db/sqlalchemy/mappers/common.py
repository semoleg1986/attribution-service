"""Маппинг общих value objects/метаданных."""

from __future__ import annotations

from src.domain.shared.entity import EntityMeta


def to_meta(*, version: int, created_at, created_by: str, updated_at, updated_by: str, archived_at, archived_by: str | None) -> EntityMeta:
    """Собирает EntityMeta из полей ORM-модели."""

    return EntityMeta(
        version=version,
        created_at=created_at,
        created_by=created_by,
        updated_at=updated_at,
        updated_by=updated_by,
        archived_at=archived_at,
        archived_by=archived_by,
    )
