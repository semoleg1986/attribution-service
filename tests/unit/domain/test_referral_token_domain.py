from datetime import UTC, datetime, timedelta

import pytest

from src.domain.errors import InvariantViolationError
from src.domain.shared.statuses import AttributionChannel, DiscountType
from src.domain.shared.value_objects import Money
from src.domain.tokens.referral_token.entity import ReferralToken


def test_referral_token_default_ttl_to_course_start() -> None:
    now = datetime.now(UTC)
    course_start = now + timedelta(days=10)

    token = ReferralToken.create(
        token="tok-1",
        channel=AttributionChannel.EMAIL,
        discount_type=DiscountType.PERCENT,
        discount_value=10,
        now=now,
        created_by="admin-1",
        course_starts_at=course_start,
    )

    assert token.expires_at == course_start


def test_referral_token_is_invalid_after_expiry() -> None:
    now = datetime.now(UTC)
    course_start = now + timedelta(minutes=1)

    token = ReferralToken.create(
        token="tok-1",
        channel=AttributionChannel.EMAIL,
        discount_type=DiscountType.FIXED,
        discount_value=20,
        now=now,
        created_by="admin-1",
        course_starts_at=course_start,
    )

    valid, discount = token.resolve_discount(
        base_amount=Money(amount=100, currency="USD"),
        now=course_start + timedelta(seconds=1),
    )

    assert valid is False
    assert discount.amount == 0


def test_discount_policy_cannot_change_after_paid_conversion() -> None:
    now = datetime.now(UTC)
    course_start = now + timedelta(days=3)

    token = ReferralToken.create(
        token="tok-1",
        channel=AttributionChannel.PARTNER,
        discount_type=DiscountType.PERCENT,
        discount_value=15,
        now=now,
        created_by="admin-1",
        course_starts_at=course_start,
    )

    token.lock_policy(changed_at=now, changed_by="system")

    with pytest.raises(InvariantViolationError):
        token.update_discount_policy(
            DiscountType.FIXED,
            30,
            changed_at=now,
            changed_by="admin-1",
        )
