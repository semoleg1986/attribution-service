from datetime import UTC, datetime

from src.application.tracking.commands.dto import (
    RecordPaidConversionCommand,
    RecordRequestedConversionCommand,
)
from src.application.tracking.handlers.tracking_handlers import (
    RecordPaidConversionHandler,
    RecordRequestedConversionHandler,
)
from src.infrastructure.db.inmemory.repositories import (
    InMemoryAttributionConversionRepository,
    InMemoryAttributionVisitRepository,
    InMemoryReferralTokenRepository,
)
from src.infrastructure.db.inmemory.uow import InMemoryRepositoryProvider, InMemoryUnitOfWork


class FakeClock:
    def __init__(self, now_value: datetime) -> None:
        self._now_value = now_value

    def now(self) -> datetime:
        return self._now_value


def _build_uow() -> InMemoryUnitOfWork:
    return InMemoryUnitOfWork(
        InMemoryRepositoryProvider(
            referral_tokens=InMemoryReferralTokenRepository(),
            visits=InMemoryAttributionVisitRepository(),
            conversions=InMemoryAttributionConversionRepository(),
        )
    )


def test_requested_then_paid_conversion_flow() -> None:
    uow = _build_uow()
    clock = FakeClock(datetime(2026, 4, 9, tzinfo=UTC))

    record_requested = RecordRequestedConversionHandler(uow=uow, clock=clock)
    record_paid = RecordPaidConversionHandler(uow=uow, clock=clock)

    requested = record_requested(
        RecordRequestedConversionCommand(
            access_grant_id="grant-1",
            course_id="course-1",
            student_id="student-1",
            parent_id=None,
            token=None,
            channel="email",
            discount_amount=20,
            discount_currency="USD",
            actor_id="svc-course",
            actor_roles=["service"],
        )
    )
    assert requested.accepted is True

    paid = record_paid(
        RecordPaidConversionCommand(
            access_grant_id="grant-1",
            paid_amount=100,
            currency="USD",
            approved_by_admin_id="admin-1",
            actor_id="svc-course",
            actor_roles=["service"],
        )
    )
    assert paid.accepted is True
