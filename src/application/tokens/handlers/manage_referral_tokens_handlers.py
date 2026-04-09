"""Handlers управления referral tokens."""

from __future__ import annotations

from datetime import timedelta

from src.application.common.dto import ReferralTokenResult
from src.application.common.mappers import to_referral_token_result
from src.application.ports.clock import Clock
from src.application.ports.id_generator import IdGenerator
from src.application.ports.unit_of_work import UnitOfWork
from src.application.tokens.commands.dto import (
    CreateReferralTokenCommand,
    DisableReferralTokenCommand,
)
from src.application.tokens.queries.dto import ListReferralTokensQuery
from src.domain.errors import NotFoundError
from src.domain.shared.statuses import AttributionChannel, DiscountType, TokenStatus
from src.domain.tokens.referral_token.entity import ReferralToken
from src.domain.tokens.referral_token.policies import ActorContext, AdminPolicy


class CreateReferralTokenHandler:
    """Создает новый referral token."""

    def __init__(self, *, uow: UnitOfWork, clock: Clock, id_generator: IdGenerator) -> None:
        self._uow = uow
        self._clock = clock
        self._id_generator = id_generator

    def __call__(self, command: CreateReferralTokenCommand) -> ReferralTokenResult:
        actor = ActorContext.from_claims(command.actor_id, command.actor_roles)
        AdminPolicy.ensure_can_manage_tokens(actor)

        now = self._clock.now()
        token_value = self._id_generator.new()
        course_starts_at = command.course_starts_at or (now + timedelta(days=30))
        token = ReferralToken.create(
            token=token_value,
            channel=AttributionChannel(command.channel),
            discount_type=DiscountType(command.discount_type),
            discount_value=command.discount_value,
            now=now,
            created_by=command.actor_id,
            course_starts_at=course_starts_at,
            course_id=command.course_id,
            campaign=command.campaign,
            expires_at=command.expires_at,
        )
        self._uow.repositories.referral_tokens.save(token)
        self._uow.commit()
        return to_referral_token_result(token)


class DisableReferralTokenHandler:
    """Отключает существующий referral token."""

    def __init__(self, *, uow: UnitOfWork, clock: Clock) -> None:
        self._uow = uow
        self._clock = clock

    def __call__(self, command: DisableReferralTokenCommand) -> ReferralTokenResult:
        actor = ActorContext.from_claims(command.actor_id, command.actor_roles)
        AdminPolicy.ensure_can_manage_tokens(actor)

        token = self._uow.repositories.referral_tokens.get(command.token)
        if token is None:
            raise NotFoundError("Реферальный токен не найден.")

        token.disable(changed_at=self._clock.now(), changed_by=command.actor_id)
        self._uow.repositories.referral_tokens.save(token)
        self._uow.commit()
        return to_referral_token_result(token)


class ListReferralTokensHandler:
    """Возвращает список referral tokens."""

    def __init__(self, *, uow: UnitOfWork) -> None:
        self._uow = uow

    def __call__(self, query: ListReferralTokensQuery) -> list[ReferralTokenResult]:
        actor = ActorContext.from_claims(query.actor_id, query.actor_roles)
        AdminPolicy.ensure_can_manage_tokens(actor)
        channel = AttributionChannel(query.channel) if query.channel else None
        status = TokenStatus(query.status) if query.status else None
        tokens = self._uow.repositories.referral_tokens.list(channel=channel, status=status)
        return [to_referral_token_result(item) for item in tokens]
