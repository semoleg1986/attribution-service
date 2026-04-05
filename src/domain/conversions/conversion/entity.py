from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.domain.errors import InvariantViolationError
from src.domain.shared.entity import EntityMeta
from src.domain.shared.statuses import AttributionChannel, ConversionStage
from src.domain.shared.value_objects import Money


@dataclass(slots=True)
class AttributionConversion:
    """
    Aggregate Root конверсии access grant в воронке атрибуции.

    :param access_grant_id: Идентификатор access grant.
    :type access_grant_id: str
    :param course_id: Идентификатор курса.
    :type course_id: str
    :param student_id: Идентификатор ученика.
    :type student_id: str
    """

    access_grant_id: str
    course_id: str
    student_id: str
    channel: AttributionChannel
    meta: EntityMeta
    token: str | None = None
    parent_id: str | None = None
    requested_recorded: bool = False
    paid_recorded: bool = False
    requested_discount: Money | None = None
    paid_amount: Money | None = None

    @classmethod
    def create(
        cls,
        access_grant_id: str,
        course_id: str,
        student_id: str,
        channel: AttributionChannel,
        created_at: datetime,
        created_by: str,
        token: str | None = None,
        parent_id: str | None = None,
    ) -> "AttributionConversion":
        """Создать новую запись конверсии."""
        return cls(
            access_grant_id=access_grant_id,
            course_id=course_id,
            student_id=student_id,
            channel=channel,
            meta=EntityMeta.create(at=created_at, actor_id=created_by),
            token=token,
            parent_id=parent_id,
        )

    def record_requested(
        self,
        changed_at: datetime,
        changed_by: str,
        discount: Money | None = None,
    ) -> ConversionStage:
        """Зафиксировать стадию requested (идемпотентно)."""
        self.requested_recorded = True
        self.requested_discount = discount
        self.meta.touch(at=changed_at, actor_id=changed_by)
        return ConversionStage.REQUESTED

    def record_paid(self, paid_amount: Money, changed_at: datetime, changed_by: str) -> ConversionStage:
        """
        Зафиксировать стадию paid.

        :raises InvariantViolationError: Если requested еще не зафиксирован.
        """
        if not self.requested_recorded:
            raise InvariantViolationError("Стадия paid невозможна без requested")
        self.paid_recorded = True
        self.paid_amount = paid_amount
        self.meta.touch(at=changed_at, actor_id=changed_by)
        return ConversionStage.PAID
