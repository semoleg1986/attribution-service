"""Извлечение actor context из Bearer JWT."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException

from src.application.ports.access_token_verifier import AccessTokenVerifier
from src.infrastructure.config.settings import Settings
from src.interface.http.wiring import get_access_token_verifier, get_settings


@dataclass(frozen=True, slots=True)
class HttpActor:
    actor_id: str
    roles: list[str]


def _decode_bearer_actor(
    authorization: str | None = Header(default=None, alias="Authorization"),
    verifier: AccessTokenVerifier = Depends(get_access_token_verifier),
) -> HttpActor:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Отсутствует Bearer token.")

    access_token = authorization.removeprefix("Bearer ").strip()
    if not access_token:
        raise HTTPException(status_code=401, detail="Пустой Bearer token.")

    try:
        claims = verifier.decode_access(access_token)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=401, detail="Некорректный access token."
        ) from exc

    sub = str(claims.get("sub", "")).strip()
    roles = claims.get("roles", [])
    if not sub or not isinstance(roles, list):
        raise HTTPException(
            status_code=401, detail="Access token не содержит обязательные claims."
        )

    return HttpActor(actor_id=sub, roles=[str(item) for item in roles])


def get_http_actor(
    authorization: str | None = Header(default=None, alias="Authorization"),
    verifier: AccessTokenVerifier = Depends(get_access_token_verifier),
) -> HttpActor:
    """Извлекает actor из Bearer access token."""

    return _decode_bearer_actor(authorization=authorization, verifier=verifier)


def get_internal_http_actor(
    x_service_token: str | None = Header(default=None, alias="X-Service-Token"),
    authorization: str | None = Header(default=None, alias="Authorization"),
    verifier: AccessTokenVerifier = Depends(get_access_token_verifier),
    settings: Settings = Depends(get_settings),
) -> HttpActor:
    """Извлекает actor для internal endpoints: service-token или Bearer."""

    if x_service_token is not None:
        if x_service_token.strip() != settings.service_token:
            raise HTTPException(status_code=401, detail="Некорректный service token.")
        return HttpActor(actor_id="internal-service", roles=["service"])

    return _decode_bearer_actor(authorization=authorization, verifier=verifier)
