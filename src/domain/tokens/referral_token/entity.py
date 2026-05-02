from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from src.domain.errors import InvariantViolationError
from src.domain.shared.entity import EntityMeta
from src.domain.shared.statuses import AttributionChannel, DiscountType, TokenStatus
from src.domain.shared.value_objects import Money


@dataclass(slots=True)
class ReferralToken:
    """
    Aggregate Root реферального токена.

    :param token: Значение токена.
    :type token: str
    :param channel: Канал привлечения.
    :type channel: AttributionChannel
    :param discount_type: Тип скидки (`percent|fixed`).
    :type discount_type: DiscountType
    :param discount_value: Значение скидки.
    :type discount_value: float
    """

    token: str
    channel: AttributionChannel
    discount_type: DiscountType
    discount_value: float
    course_id: str | None
    status: TokenStatus
    expires_at: datetime
    meta: EntityMeta
    campaign: str | None = None
    source: str | None = None
    medium: str | None = None
    policy_locked: bool = False

    @classmethod
    def create(
        cls,
        token: str,
        channel: AttributionChannel,
        discount_type: DiscountType,
        discount_value: float,
        now: datetime,
        created_by: str,
        course_starts_at: datetime,
        course_id: str | None = None,
        campaign: str | None = None,
        source: str | None = None,
        medium: str | None = None,
        expires_at: datetime | None = None,
    ) -> "ReferralToken":
        """
        Создать токен с TTL по умолчанию до начала курса.

        :raises InvariantViolationError: Если скидка или срок действия невалидны.
        """
        if discount_value < 0:
            raise InvariantViolationError("Значение скидки не может быть отрицательным")
        effective_expires_at = expires_at or course_starts_at
        if effective_expires_at <= now:
            raise InvariantViolationError("Срок действия токена должен быть в будущем")
        return cls(
            token=token,
            channel=channel,
            discount_type=discount_type,
            discount_value=discount_value,
            course_id=course_id,
            status=TokenStatus.ACTIVE,
            expires_at=effective_expires_at,
            meta=EntityMeta.create(at=now, actor_id=created_by),
            campaign=campaign,
            source=source,
            medium=medium,
        )

    def is_valid(self, now: datetime) -> bool:
        """Проверить, что токен активен и не истек."""
        if self.status != TokenStatus.ACTIVE:
            return False
        if now >= self.expires_at:
            return False
        return True

    def disable(self, changed_at: datetime, changed_by: str) -> None:
        """Отключить токен вручную."""
        self.status = TokenStatus.DISABLED
        self.meta.touch(at=changed_at, actor_id=changed_by)

    def mark_expired(self, changed_at: datetime) -> None:
        """Перевести токен в состояние expired."""
        self.status = TokenStatus.EXPIRED
        self.meta.touch(at=changed_at, actor_id="system")

    def lock_policy(self, changed_at: datetime, changed_by: str) -> None:
        """Зафиксировать discount policy после paid-конверсии."""
        self.policy_locked = True
        self.meta.touch(at=changed_at, actor_id=changed_by)

    def update_discount_policy(
        self,
        discount_type: DiscountType,
        discount_value: float,
        changed_at: datetime,
        changed_by: str,
    ) -> None:
        """
        Обновить policy скидки, пока она не зафиксирована.

        :raises InvariantViolationError: Если policy уже заблокирована.
        """
        if self.policy_locked:
            raise InvariantViolationError(
                "Политику скидки нельзя менять после paid-конверсии"
            )
        if discount_value < 0:
            raise InvariantViolationError("Значение скидки не может быть отрицательным")
        self.discount_type = discount_type
        self.discount_value = discount_value
        self.meta.touch(at=changed_at, actor_id=changed_by)

    def resolve_discount(self, base_amount: Money, now: datetime) -> tuple[bool, Money]:
        """
        Рассчитать скидку по токену.

        :param base_amount: Базовая сумма.
        :type base_amount: Money
        :param now: Момент расчета.
        :type now: datetime
        :return: (валидность токена, размер скидки).
        :rtype: tuple[bool, Money]
        """
        if not self.is_valid(now):
            return False, Money(amount=0.0, currency=base_amount.currency)

        if self.discount_type == DiscountType.FIXED:
            discount = min(self.discount_value, base_amount.amount)
            return True, Money(amount=discount, currency=base_amount.currency)

        if self.discount_value > 100:
            raise InvariantViolationError("Процент скидки не может быть больше 100")
        discount = base_amount.amount * (self.discount_value / 100)
        return True, Money(amount=discount, currency=base_amount.currency)
