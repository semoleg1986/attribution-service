from datetime import UTC, datetime, timedelta

from tests.unit.interface._auth_helpers import auth_headers, build_client


def test_admin_can_create_list_and_disable_token() -> None:
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

    listed = client.get(
        "/v1/admin/referral-tokens?channel=email&status=active",
        headers=auth_headers(sub="admin-1", roles=["admin"]),
    )
    assert listed.status_code == 200, listed.text
    assert len(listed.json()["items"]) == 1

    disabled = client.post(
        f"/v1/admin/referral-tokens/{token}/disable",
        headers=auth_headers(sub="admin-1", roles=["admin"]),
    )
    assert disabled.status_code == 200, disabled.text
    assert disabled.json()["status"] == "disabled"


def test_non_admin_cannot_create_token() -> None:
    client = build_client()
    denied = client.post(
        "/v1/admin/referral-tokens",
        json={
            "channel": "email",
            "discount_type": "fixed",
            "discount_value": 10,
            "course_id": "course-1",
        },
        headers=auth_headers(sub="teacher-1", roles=["teacher"]),
    )
    assert denied.status_code == 403, denied.text


def test_admin_create_token_rejects_naive_course_starts_at() -> None:
    client = build_client()

    response = client.post(
        "/v1/admin/referral-tokens",
        json={
            "channel": "email",
            "campaign": "spring",
            "course_id": "course-1",
            "discount_type": "fixed",
            "discount_value": 25,
            "course_starts_at": "2026-09-01T16:00:00",
        },
        headers=auth_headers(sub="admin-1", roles=["admin"]),
    )
    assert response.status_code == 422, response.text
    assert (
        "course_starts_at должен содержать timezone offset" in response.json()["detail"]
    )


def test_admin_create_token_rejects_naive_expires_at() -> None:
    client = build_client()

    response = client.post(
        "/v1/admin/referral-tokens",
        json={
            "channel": "email",
            "campaign": "spring",
            "course_id": "course-1",
            "discount_type": "fixed",
            "discount_value": 25,
            "course_starts_at": (datetime.now(UTC) + timedelta(days=10)).isoformat(),
            "expires_at": "2026-08-01T10:00:00",
        },
        headers=auth_headers(sub="admin-1", roles=["admin"]),
    )
    assert response.status_code == 422, response.text
    assert "expires_at должен содержать timezone offset" in response.json()["detail"]
