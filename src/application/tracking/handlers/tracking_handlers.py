"""Handlers tracking/conversion use-cases."""

from __future__ import annotations

from src.application.common.dto import (
    ConversionResult,
    ResolveDiscountResult,
    TrackClickResult,
)
from src.application.common.mappers import to_money_result
from src.application.ports.clock import Clock
from src.application.ports.id_generator import IdGenerator
from src.application.ports.unit_of_work import UnitOfWork
from src.application.tracking.commands.dto import (
    RecordPaidConversionCommand,
    RecordRequestedConversionCommand,
    TrackVisitCommand,
)
from src.application.tracking.queries.dto import ResolveDiscountQuery
from src.domain.conversions.conversion.entity import AttributionConversion
from src.domain.conversions.conversion.policies import InternalPolicy
from src.domain.errors import NotFoundError
from src.domain.shared.statuses import AttributionChannel
from src.domain.shared.value_objects import Money
from src.domain.tokens.referral_token.policies import ActorContext
from src.domain.visits.visit.entity import AttributionVisit


class TrackVisitHandler:
    """Фиксирует click по реферальной ссылке."""

    def __init__(
        self, *, uow: UnitOfWork, clock: Clock, id_generator: IdGenerator
    ) -> None:
        self._uow = uow
        self._clock = clock
        self._id_generator = id_generator

    def __call__(self, command: TrackVisitCommand) -> TrackClickResult:
        token = self._uow.repositories.referral_tokens.get(command.token)
        channel = token.channel if token is not None else AttributionChannel.OTHER
        visit = AttributionVisit.create(
            visit_id=self._id_generator.new(),
            token=command.token,
            channel=channel,
            clicked_at=self._clock.now(),
            created_by="public",
            parent_id=command.parent_id,
            anonymous_id=command.anonymous_id,
            source_url=command.source_url,
        )
        self._uow.repositories.visits.add(visit)
        self._uow.commit()
        return TrackClickResult(accepted=True)


class ResolveDiscountHandler:
    """Возвращает снимок скидки и атрибуции для course_service."""

    def __init__(self, *, uow: UnitOfWork, clock: Clock) -> None:
        self._uow = uow
        self._clock = clock

    def __call__(self, query: ResolveDiscountQuery) -> ResolveDiscountResult:
        actor = ActorContext.from_claims(query.actor_id, query.actor_roles)
        InternalPolicy.ensure_can_call_internal(actor)

        if query.referral_token is None:
            return ResolveDiscountResult(
                valid=False,
                token=None,
                channel=(query.channel or AttributionChannel.OTHER.value),
                campaign=None,
                discount_type="fixed",
                discount_value=0.0,
                discount=to_money_result(Money(amount=0.0, currency="USD")),
            )

        token = self._uow.repositories.referral_tokens.get(query.referral_token)
        if token is None:
            return ResolveDiscountResult(
                valid=False,
                token=query.referral_token,
                channel=(query.channel or AttributionChannel.OTHER.value),
                campaign=None,
                discount_type="fixed",
                discount_value=0.0,
                discount=to_money_result(Money(amount=0.0, currency="USD")),
            )

        if token.course_id is not None and token.course_id != query.course_id:
            return ResolveDiscountResult(
                valid=False,
                token=token.token,
                channel=token.channel.value,
                campaign=token.campaign,
                discount_type="fixed",
                discount_value=0.0,
                discount=to_money_result(Money(amount=0.0, currency="USD")),
            )

        valid, discount = token.resolve_discount(
            base_amount=Money(amount=100.0, currency="USD"),
            now=self._clock.now(),
        )
        return ResolveDiscountResult(
            valid=valid,
            token=token.token,
            channel=token.channel.value,
            campaign=token.campaign,
            discount_type=token.discount_type.value,
            discount_value=float(token.discount_value),
            discount=to_money_result(discount),
        )


class RecordRequestedConversionHandler:
    """Записывает стадию requested (идемпотентно)."""

    def __init__(self, *, uow: UnitOfWork, clock: Clock) -> None:
        self._uow = uow
        self._clock = clock

    def __call__(self, command: RecordRequestedConversionCommand) -> ConversionResult:
        actor = ActorContext.from_claims(command.actor_id, command.actor_roles)
        InternalPolicy.ensure_can_call_internal(actor)

        now = self._clock.now()
        conversion = self._uow.repositories.conversions.get(command.access_grant_id)
        if conversion is None:
            conversion = AttributionConversion.create(
                access_grant_id=command.access_grant_id,
                course_id=command.course_id,
                student_id=command.student_id,
                channel=AttributionChannel(command.channel),
                created_at=now,
                created_by=command.actor_id,
                token=command.token,
                parent_id=command.parent_id,
            )

        discount = None
        if (
            command.discount_amount is not None
            and command.discount_currency is not None
        ):
            discount = Money(
                amount=command.discount_amount, currency=command.discount_currency
            )

        conversion.record_requested(
            changed_at=now, changed_by=command.actor_id, discount=discount
        )
        self._uow.repositories.conversions.save(conversion)
        self._uow.commit()
        return ConversionResult(accepted=True)


class RecordPaidConversionHandler:
    """Записывает стадию paid и фиксирует политику токена."""

    def __init__(self, *, uow: UnitOfWork, clock: Clock) -> None:
        self._uow = uow
        self._clock = clock

    def __call__(self, command: RecordPaidConversionCommand) -> ConversionResult:
        actor = ActorContext.from_claims(command.actor_id, command.actor_roles)
        InternalPolicy.ensure_can_call_internal(actor)

        conversion = self._uow.repositories.conversions.get(command.access_grant_id)
        if conversion is None:
            raise NotFoundError("Conversion по access_grant_id не найдена.")

        changed_by = command.approved_by_admin_id or command.actor_id
        now = self._clock.now()
        conversion.record_paid(
            paid_amount=Money(amount=command.paid_amount, currency=command.currency),
            changed_at=now,
            changed_by=changed_by,
        )

        if conversion.token:
            token = self._uow.repositories.referral_tokens.get(conversion.token)
            if token is not None and not token.policy_locked:
                token.lock_policy(changed_at=now, changed_by=changed_by)
                self._uow.repositories.referral_tokens.save(token)

        self._uow.repositories.conversions.save(conversion)
        self._uow.commit()
        return ConversionResult(accepted=True)
