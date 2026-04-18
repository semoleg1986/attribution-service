from __future__ import annotations

import os

from tests.unit.interface._auth_helpers import build_client


def test_internal_resolve_accepts_service_token_header() -> None:
    os.environ["ATTR_SERVICE_TOKEN"] = "svc-internal-token"
    client = build_client()

    response = client.post(
        "/v1/internal/discount/resolve",
        json={
            "course_id": "course-1",
            "referral_token": None,
            "channel": "email",
        },
        headers={"X-Service-Token": "svc-internal-token"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["valid"] is False
    assert payload["discount_type"] == "fixed"
    assert payload["discount_value"] == 0.0


def test_internal_resolve_rejects_wrong_service_token() -> None:
    os.environ["ATTR_SERVICE_TOKEN"] = "svc-internal-token"
    client = build_client()

    response = client.post(
        "/v1/internal/discount/resolve",
        json={
            "course_id": "course-1",
            "referral_token": None,
            "channel": "email",
        },
        headers={"X-Service-Token": "wrong-token"},
    )

    assert response.status_code == 401, response.text
