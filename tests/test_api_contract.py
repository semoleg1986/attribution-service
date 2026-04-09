from __future__ import annotations

import base64
import json
import os
from datetime import UTC, datetime, timedelta

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient
import jwt

from src.interface.http.app import create_app
from src.interface.http.wiring import get_runtime

_PRIVATE_KEY = Ed25519PrivateKey.generate()
_PUBLIC_KEY = _PRIVATE_KEY.public_key()
_AUDIENCE = "platform_clients"


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _jwks_json() -> str:
    raw = _PUBLIC_KEY.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return json.dumps(
        {
            "keys": [
                {
                    "kty": "OKP",
                    "crv": "Ed25519",
                    "x": _b64url(raw),
                    "alg": "EdDSA",
                    "use": "sig",
                    "kid": "attr-test-kid",
                }
            ]
        }
    )


def _access_token(*, sub: str, roles: list[str]) -> str:
    now = datetime.now(UTC)
    claims = {
        "iss": "auth_service",
        "aud": _AUDIENCE,
        "typ": "access",
        "sub": sub,
        "jti": f"jti-{sub}",
        "roles": roles,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=30)).timestamp()),
    }
    return jwt.encode(
        claims,
        _PRIVATE_KEY,
        algorithm="EdDSA",
        headers={"kid": "attr-test-kid", "typ": "JWT"},
    )


def _auth_headers(*, sub: str, roles: list[str]) -> dict[str, str]:
    return {"Authorization": f"Bearer {_access_token(sub=sub, roles=roles)}"}


def _client() -> TestClient:
    os.environ["ATTR_USE_INMEMORY"] = "1"
    os.environ["ATTR_AUTH_JWKS_JSON"] = _jwks_json()
    os.environ["ATTR_AUTH_ISSUER"] = "auth_service"
    os.environ["ATTR_AUTH_AUDIENCE"] = _AUDIENCE
    get_runtime.cache_clear()
    return TestClient(create_app())


def test_healthz() -> None:
    response = _client().get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_full_attribution_flow() -> None:
    client = _client()

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
        headers=_auth_headers(sub="admin-1", roles=["admin"]),
    )
    assert created.status_code == 201, created.text
    token = created.json()["token"]

    listed = client.get(
        "/v1/admin/referral-tokens?channel=email&status=active",
        headers=_auth_headers(sub="admin-1", roles=["admin"]),
    )
    assert listed.status_code == 200, listed.text
    assert len(listed.json()["items"]) == 1

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
        headers=_auth_headers(sub="svc-course", roles=["service"]),
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
        headers=_auth_headers(sub="svc-course", roles=["service"]),
    )
    assert requested.status_code == 202, requested.text

    paid = client.post(
        "/v1/internal/conversions/paid",
        json={
            "access_grant_id": "grant-1",
            "paid_amount": {"amount": 100, "currency": "USD"},
            "approved_by_admin_id": "admin-1",
        },
        headers=_auth_headers(sub="svc-course", roles=["service"]),
    )
    assert paid.status_code == 202, paid.text

    report = client.get(
        "/v1/admin/reports/channels?date_from=2026-01-01&date_to=2026-12-31",
        headers=_auth_headers(sub="admin-1", roles=["admin"]),
    )
    assert report.status_code == 200, report.text
    email_row = next(item for item in report.json()["items"] if item["channel"] == "email")
    assert email_row["clicks"] == 1
    assert email_row["requested"] == 1
    assert email_row["paid"] == 1

    disabled = client.post(
        f"/v1/admin/referral-tokens/{token}/disable",
        headers=_auth_headers(sub="admin-1", roles=["admin"]),
    )
    assert disabled.status_code == 200, disabled.text
    assert disabled.json()["status"] == "disabled"


def test_non_admin_cannot_create_token() -> None:
    client = _client()
    denied = client.post(
        "/v1/admin/referral-tokens",
        json={
            "channel": "email",
            "discount_type": "fixed",
            "discount_value": 10,
            "course_id": "course-1",
        },
        headers=_auth_headers(sub="teacher-1", roles=["teacher"]),
    )
    assert denied.status_code == 403, denied.text
