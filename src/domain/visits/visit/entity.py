from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.domain.shared.entity import EntityMeta
from src.domain.shared.statuses import AttributionChannel


@dataclass(slots=True)
class AttributionVisit:
    """
    Факт перехода (click) по токену.

    :param visit_id: Идентификатор факта.
    :type visit_id: str
    :param token: Реферальный токен.
    :type token: str
    :param channel: Канал привлечения.
    :type channel: AttributionChannel
    """

    visit_id: str
    token: str
    channel: AttributionChannel
    clicked_at: datetime
    meta: EntityMeta
    parent_id: str | None = None
    anonymous_id: str | None = None
    source_url: str | None = None

    @classmethod
    def create(
        cls,
        visit_id: str,
        token: str,
        channel: AttributionChannel,
        clicked_at: datetime,
        created_by: str,
        parent_id: str | None = None,
        anonymous_id: str | None = None,
        source_url: str | None = None,
    ) -> "AttributionVisit":
        """Создать новый факт перехода."""
        return cls(
            visit_id=visit_id,
            token=token,
            channel=channel,
            clicked_at=clicked_at,
            meta=EntityMeta.create(at=clicked_at, actor_id=created_by),
            parent_id=parent_id,
            anonymous_id=anonymous_id,
            source_url=source_url,
        )
