from datetime import UTC, datetime

import pytest

from src.domain.conversions.conversion.entity import AttributionConversion
from src.domain.errors import InvariantViolationError
from src.domain.shared.statuses import AttributionChannel
from src.domain.shared.value_objects import Money


def test_paid_conversion_requires_requested_stage() -> None:
    now = datetime.now(UTC)
    conversion = AttributionConversion.create(
        access_grant_id="g-1",
        course_id="course-1",
        student_id="student-1",
        channel=AttributionChannel.ADS,
        created_at=now,
        created_by="course-service",
    )

    with pytest.raises(InvariantViolationError):
        conversion.record_paid(
            Money(amount=120, currency="USD"),
            changed_at=now,
            changed_by="course-service",
        )


def test_conversion_meta_version_increments() -> None:
    now = datetime.now(UTC)
    conversion = AttributionConversion.create(
        access_grant_id="g-1",
        course_id="course-1",
        student_id="student-1",
        channel=AttributionChannel.ADS,
        created_at=now,
        created_by="course-service",
    )
    v1 = conversion.meta.version

    conversion.record_requested(changed_at=now, changed_by="course-service")

    assert conversion.meta.version == v1 + 1
