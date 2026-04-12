"""Маппер AttributionConversion <-> AttributionConversionModel."""

from __future__ import annotations

from src.domain.conversions.conversion.entity import AttributionConversion
from src.domain.shared.statuses import AttributionChannel
from src.domain.shared.value_objects import Money
from src.infrastructure.db.sqlalchemy.mappers.common import to_meta
from src.infrastructure.db.sqlalchemy.models import AttributionConversionModel


def to_domain(model: AttributionConversionModel) -> AttributionConversion:
    """Преобразует ORM-модель в доменный агрегат."""

    requested_discount = None
    if model.requested_discount_amount is not None and model.requested_discount_currency is not None:
        requested_discount = Money(
            amount=model.requested_discount_amount,
            currency=model.requested_discount_currency,
        )

    paid_amount = None
    if model.paid_amount is not None and model.paid_currency is not None:
        paid_amount = Money(amount=model.paid_amount, currency=model.paid_currency)

    return AttributionConversion(
        access_grant_id=model.access_grant_id,
        course_id=model.course_id,
        student_id=model.student_id,
        channel=AttributionChannel(model.channel),
        meta=to_meta(
            version=model.version,
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by,
            archived_at=model.archived_at,
            archived_by=model.archived_by,
        ),
        token=model.token,
        parent_id=model.parent_id,
        requested_recorded=model.requested_recorded,
        paid_recorded=model.paid_recorded,
        requested_discount=requested_discount,
        paid_amount=paid_amount,
    )


def apply_to_model(entity: AttributionConversion, model: AttributionConversionModel) -> None:
    """Копирует доменные поля в ORM-модель."""

    model.access_grant_id = entity.access_grant_id
    model.course_id = entity.course_id
    model.student_id = entity.student_id
    model.channel = entity.channel.value
    model.token = entity.token
    model.parent_id = entity.parent_id
    model.requested_recorded = entity.requested_recorded
    model.paid_recorded = entity.paid_recorded

    model.requested_discount_amount = (
        entity.requested_discount.amount if entity.requested_discount is not None else None
    )
    model.requested_discount_currency = (
        entity.requested_discount.currency if entity.requested_discount is not None else None
    )
    model.paid_amount = entity.paid_amount.amount if entity.paid_amount is not None else None
    model.paid_currency = entity.paid_amount.currency if entity.paid_amount is not None else None

    model.version = entity.meta.version
    model.created_at = entity.meta.created_at
    model.created_by = entity.meta.created_by
    model.updated_at = entity.meta.updated_at
    model.updated_by = entity.meta.updated_by
    model.archived_at = entity.meta.archived_at
    model.archived_by = entity.meta.archived_by
