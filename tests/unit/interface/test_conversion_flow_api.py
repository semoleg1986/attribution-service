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


def test_public_redirect_alias_tracks_click_and_redirects() -> None:
    client = build_client()

    created = client.post(
        "/v1/admin/referral-tokens",
        json={
            "channel": "email",
            "campaign": "redirect-spring",
            "course_id": "course-1",
            "discount_type": "fixed",
            "discount_value": 25,
            "course_starts_at": (datetime.now(UTC) + timedelta(days=10)).isoformat(),
        },
        headers=auth_headers(sub="admin-1", roles=["admin"]),
    )
    assert created.status_code == 201, created.text
    token = created.json()["token"]

    redirect = client.get(
        f"/r/{token}",
        params={
            "anonymous_id": "anon-r-1",
            "source_url": "https://example.com/landing",
            "redirect_to": "https://example.com/checkout",
        },
        follow_redirects=False,
    )
    assert redirect.status_code == 307, redirect.text
    assert redirect.headers["location"] == "https://example.com/checkout"

    report = client.get(
        "/v1/admin/reports/channels?date_from=2026-01-01&date_to=2026-12-31",
        headers=auth_headers(sub="admin-1", roles=["admin"]),
    )
    assert report.status_code == 200, report.text
    email_row = next(
        item for item in report.json()["items"] if item["channel"] == "email"
    )
    assert email_row["clicks"] == 1


def test_public_redirect_alias_rejects_unsafe_redirect_target() -> None:
    client = build_client()

    created = client.post(
        "/v1/admin/referral-tokens",
        json={
            "channel": "email",
            "campaign": "unsafe-redirect",
            "course_id": "course-1",
            "discount_type": "fixed",
            "discount_value": 25,
            "course_starts_at": (datetime.now(UTC) + timedelta(days=10)).isoformat(),
        },
        headers=auth_headers(sub="admin-1", roles=["admin"]),
    )
    assert created.status_code == 201, created.text
    token = created.json()["token"]

    redirect = client.get(
        f"/r/{token}",
        params={"redirect_to": "/relative/path"},
        follow_redirects=False,
    )
    assert redirect.status_code == 400, redirect.text
    assert "redirect_to" in redirect.json()["detail"]


def test_campaign_stats_aggregates_by_channel_and_campaign() -> None:
    client = build_client()

    spring = client.post(
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
    assert spring.status_code == 201, spring.text
    spring_token = spring.json()["token"]

    may = client.post(
        "/v1/admin/referral-tokens",
        json={
            "channel": "email",
            "campaign": "may",
            "course_id": "course-2",
            "discount_type": "fixed",
            "discount_value": 10,
            "course_starts_at": (datetime.now(UTC) + timedelta(days=10)).isoformat(),
        },
        headers=auth_headers(sub="admin-1", roles=["admin"]),
    )
    assert may.status_code == 201, may.text
    may_token = may.json()["token"]

    for token in (spring_token, spring_token, may_token):
        click = client.post(
            f"/v1/public/referrals/{token}/click",
            json={"anonymous_id": f"anon-{token}", "source_url": "https://example.com"},
        )
        assert click.status_code == 202, click.text

    requested_1 = client.post(
        "/v1/internal/conversions/requested",
        json={
            "access_grant_id": "grant-spring-1",
            "course_id": "course-1",
            "student_id": "student-1",
            "token": spring_token,
            "channel": "email",
            "discount": {"amount": 25, "currency": "USD"},
        },
        headers=auth_headers(sub="svc-course", roles=["service"]),
    )
    assert requested_1.status_code == 202, requested_1.text

    paid_1 = client.post(
        "/v1/internal/conversions/paid",
        json={
            "access_grant_id": "grant-spring-1",
            "paid_amount": {"amount": 100, "currency": "USD"},
            "approved_by_admin_id": "admin-1",
        },
        headers=auth_headers(sub="svc-course", roles=["service"]),
    )
    assert paid_1.status_code == 202, paid_1.text

    requested_2 = client.post(
        "/v1/internal/conversions/requested",
        json={
            "access_grant_id": "grant-may-1",
            "course_id": "course-2",
            "student_id": "student-2",
            "token": may_token,
            "channel": "email",
            "discount": {"amount": 10, "currency": "USD"},
        },
        headers=auth_headers(sub="svc-course", roles=["service"]),
    )
    assert requested_2.status_code == 202, requested_2.text

    report = client.get(
        "/v1/admin/campaigns/stats?date_from=2026-01-01&date_to=2026-12-31&channel=email&limit=10&offset=0",
        headers=auth_headers(sub="admin-1", roles=["admin"]),
    )
    assert report.status_code == 200, report.text
    payload = report.json()
    assert payload["limit"] == 10
    assert payload["offset"] == 0
    assert payload["total"] == 2

    spring_row = next(item for item in payload["items"] if item["campaign"] == "spring")
    assert spring_row["channel"] == "email"
    assert spring_row["clicks"] == 2
    assert spring_row["requested"] == 1
    assert spring_row["paid"] == 1
    assert spring_row["gross_revenue"]["amount"] == 100.0
    assert spring_row["discount_total"]["amount"] == 25.0

    may_row = next(item for item in payload["items"] if item["campaign"] == "may")
    assert may_row["clicks"] == 1
    assert may_row["requested"] == 1
    assert may_row["paid"] == 0
    assert may_row["gross_revenue"]["amount"] == 0.0
    assert may_row["discount_total"]["amount"] == 10.0


def test_campaign_stats_csv_export() -> None:
    client = build_client()

    created = client.post(
        "/v1/admin/referral-tokens",
        json={
            "channel": "email",
            "campaign": "csv-spring",
            "course_id": "course-1",
            "discount_type": "fixed",
            "discount_value": 15,
            "course_starts_at": (datetime.now(UTC) + timedelta(days=10)).isoformat(),
        },
        headers=auth_headers(sub="admin-1", roles=["admin"]),
    )
    assert created.status_code == 201, created.text
    token = created.json()["token"]

    click = client.post(
        f"/v1/public/referrals/{token}/click",
        json={"anonymous_id": "anon-csv-1", "source_url": "https://example.com"},
    )
    assert click.status_code == 202, click.text

    requested = client.post(
        "/v1/internal/conversions/requested",
        json={
            "access_grant_id": "grant-csv-1",
            "course_id": "course-1",
            "student_id": "student-1",
            "token": token,
            "channel": "email",
            "discount": {"amount": 15, "currency": "USD"},
        },
        headers=auth_headers(sub="svc-course", roles=["service"]),
    )
    assert requested.status_code == 202, requested.text

    exported = client.get(
        "/v1/admin/campaigns/stats.csv?date_from=2026-01-01&date_to=2026-12-31&channel=email",
        headers=auth_headers(sub="admin-1", roles=["admin"]),
    )
    assert exported.status_code == 200, exported.text
    assert exported.headers["content-type"].startswith("text/csv")
    assert 'attachment; filename="campaign-stats.csv"' in exported.headers.get(
        "content-disposition", ""
    )
    assert "channel,campaign,clicks,requested,paid" in exported.text
    assert "email,csv-spring,1,1,0,0.0,USD,15.0,USD" in exported.text
