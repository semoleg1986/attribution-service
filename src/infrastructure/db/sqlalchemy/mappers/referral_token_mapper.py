"""Маппер ReferralToken <-> ReferralTokenModel."""

from __future__ import annotations

from src.domain.shared.statuses import AttributionChannel, DiscountType, TokenStatus
from src.domain.tokens.referral_token.entity import ReferralToken
from src.infrastructure.db.sqlalchemy.mappers.common import to_meta
from src.infrastructure.db.sqlalchemy.models import ReferralTokenModel


def to_domain(model: ReferralTokenModel) -> ReferralToken:
    """Преобразует ORM-модель в доменный агрегат."""

    return ReferralToken(
        token=model.token,
        channel=AttributionChannel(model.channel),
        discount_type=DiscountType(model.discount_type),
        discount_value=model.discount_value,
        course_id=model.course_id,
        status=TokenStatus(model.status),
        expires_at=model.expires_at,
        meta=to_meta(
            version=model.version,
            created_at=model.created_at,
            created_by=model.created_by,
            updated_at=model.updated_at,
            updated_by=model.updated_by,
            archived_at=model.archived_at,
            archived_by=model.archived_by,
        ),
        campaign=model.campaign,
        source=model.source,
        medium=model.medium,
        policy_locked=model.policy_locked,
    )


def apply_to_model(entity: ReferralToken, model: ReferralTokenModel) -> None:
    """Копирует доменные поля в ORM-модель."""

    model.token = entity.token
    model.channel = entity.channel.value
    model.discount_type = entity.discount_type.value
    model.discount_value = entity.discount_value
    model.course_id = entity.course_id
    model.status = entity.status.value
    model.expires_at = entity.expires_at
    model.campaign = entity.campaign
    model.source = entity.source
    model.medium = entity.medium
    model.policy_locked = entity.policy_locked

    model.version = entity.meta.version
    model.created_at = entity.meta.created_at
    model.created_by = entity.meta.created_by
    model.updated_at = entity.meta.updated_at
    model.updated_by = entity.meta.updated_by
    model.archived_at = entity.meta.archived_at
    model.archived_by = entity.meta.archived_by
