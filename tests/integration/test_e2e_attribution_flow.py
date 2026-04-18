from __future__ import annotations

import base64
import json
import os
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from fastapi.testclient import TestClient

from src.interface.http.app import create_app
from src.interface.http.wiring import get_runtime

pytestmark = pytest.mark.integration

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
                    "kid": "attr-int-kid",
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
        headers={"kid": "attr-int-kid", "typ": "JWT"},
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


def test_e2e_referral_conversion_flow() -> None:
    client = _client()

    created = client.post(
        "/v1/admin/referral-tokens",
        json={
            "channel": "ads",
            "discount_type": "fixed",
            "discount_value": 15,
            "course_id": "course-1",
            "campaign": "spring-2026",
        },
        headers=_auth_headers(sub="admin-1", roles=["admin"]),
    )
    assert created.status_code == 201, created.text
    token = created.json()["token"]

    click = client.post(
        f"/v1/public/referrals/{token}/click",
        json={"anonymous_id": "anon-1", "parent_id": "parent-1"},
    )
    assert click.status_code == 202, click.text
    assert click.json()["accepted"] is True

    resolved = client.post(
        "/v1/internal/discount/resolve",
        json={
            "course_id": "course-1",
            "referral_token": token,
            "parent_id": "parent-1",
        },
        headers=_auth_headers(sub="course-service", roles=["course_service"]),
    )
    assert resolved.status_code == 200, resolved.text
    body = resolved.json()
    assert body["valid"] is True
    assert body["token"] == token
    assert body["discount"]["amount"] == 15

    requested = client.post(
        "/v1/internal/conversions/requested",
        json={
            "access_grant_id": "ag-1",
            "course_id": "course-1",
            "student_id": "student-1",
            "parent_id": "parent-1",
            "token": token,
            "channel": "ads",
            "discount": body["discount"],
        },
        headers=_auth_headers(sub="course-service", roles=["course_service"]),
    )
    assert requested.status_code == 202, requested.text
    assert requested.json()["accepted"] is True

    paid = client.post(
        "/v1/internal/conversions/paid",
        json={
            "access_grant_id": "ag-1",
            "paid_amount": {"amount": 85, "currency": "USD"},
            "approved_by_admin_id": "admin-1",
        },
        headers=_auth_headers(sub="course-service", roles=["course_service"]),
    )
    assert paid.status_code == 202, paid.text
    assert paid.json()["accepted"] is True

    date_str = datetime.now(UTC).date().isoformat()
    report = client.get(
        f"/v1/admin/reports/channels?date_from={date_str}&date_to={date_str}",
        headers=_auth_headers(sub="admin-1", roles=["admin"]),
    )
    assert report.status_code == 200, report.text
    ads_item = next(item for item in report.json()["items"] if item["channel"] == "ads")
    assert ads_item["clicks"] >= 1
    assert ads_item["requested"] >= 1
    assert ads_item["paid"] >= 1
