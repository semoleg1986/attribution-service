"""Маппер AttributionVisit <-> AttributionVisitModel."""

from __future__ import annotations

from src.domain.shared.statuses import AttributionChannel
from src.domain.visits.visit.entity import AttributionVisit
from src.infrastructure.db.sqlalchemy.mappers.common import to_meta
from src.infrastructure.db.sqlalchemy.models import AttributionVisitModel


def to_domain(model: AttributionVisitModel) -> AttributionVisit:
    """Преобразует ORM-модель в доменную сущность."""

    return AttributionVisit(
        visit_id=model.visit_id,
        token=model.token,
        channel=AttributionChannel(model.channel),
        clicked_at=model.clicked_at,
        meta=to_meta(
            version=model.version,
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by,
            archived_at=model.archived_at,
            archived_by=model.archived_by,
        ),
        parent_id=model.parent_id,
        anonymous_id=model.anonymous_id,
        source_url=model.source_url,
    )


def apply_to_model(entity: AttributionVisit, model: AttributionVisitModel) -> None:
    """Копирует доменные поля в ORM-модель."""

    model.visit_id = entity.visit_id
    model.token = entity.token
    model.channel = entity.channel.value
    model.clicked_at = entity.clicked_at
    model.parent_id = entity.parent_id
    model.anonymous_id = entity.anonymous_id
    model.source_url = entity.source_url

    model.version = entity.meta.version
    model.created_at = entity.meta.created_at
    model.created_by = entity.meta.created_by
    model.updated_at = entity.meta.updated_at
    model.updated_by = entity.meta.updated_by
    model.archived_at = entity.meta.archived_at
    model.archived_by = entity.meta.archived_by
