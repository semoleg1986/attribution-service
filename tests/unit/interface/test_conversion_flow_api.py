from datetime import UTC, datetime, timedelta

from tests.unit.interface._auth_helpers import auth_headers, build_client


def test_public_click_internal_resolve_and_conversion_report_flow() -> None:
    client = build_client()

    created = client.post(
        "/v1/admin/referral-tokens",
        json={
            "channel": "email",
            "campaign": "spring",
            "course_id": "course-1",
            "discount_type": "fixed",
            "discount_value": 25,
            "course_starts_at": (datetime.now(UTC) + timedelta(days=10)).isoformat(),
        },
        headers=auth_headers(sub="admin-1", roles=["admin"]),
    )
    assert created.status_code == 201, created.text
    token = created.json()["token"]

    click = client.post(
        f"/v1/public/referrals/{token}/click",
        json={"anonymous_id": "anon-1", "source_url": "https://example.com"},
    )
    assert click.status_code == 202, click.text
    assert click.json()["accepted"] is True

    resolved = client.post(
        "/v1/internal/discount/resolve",
        json={
            "course_id": "course-1",
            "referral_token": token,
            "channel": "email",
        },
        headers=auth_headers(sub="svc-course", roles=["service"]),
    )
    assert resolved.status_code == 200, resolved.text
    assert resolved.json()["valid"] is True

    requested = client.post(
        "/v1/internal/conversions/requested",
        json={
            "access_grant_id": "grant-1",
            "course_id": "course-1",
            "student_id": "student-1",
            "token": token,
            "channel": "email",
            "discount": {"amount": 25, "currency": "USD"},
        },
        headers=auth_headers(sub="svc-course", roles=["service"]),
    )
    assert requested.status_code == 202, requested.text

    paid = client.post(
        "/v1/internal/conversions/paid",
        json={
            "access_grant_id": "grant-1",
            "paid_amount": {"amount": 100, "currency": "USD"},
            "approved_by_admin_id": "admin-1",
        },
        headers=auth_headers(sub="svc-course", roles=["service"]),
    )
    assert paid.status_code == 202, paid.text

    report = client.get(
        "/v1/admin/reports/channels?date_from=2026-01-01&date_to=2026-12-31",
        headers=auth_headers(sub="admin-1", roles=["admin"]),
    )
    assert report.status_code == 200, report.text
    email_row = next(
        item for item in report.json()["items"] if item["channel"] == "email"
    )
    assert email_row["clicks"] == 1
    assert email_row["requested"] == 1
    assert email_row["paid"] == 1
