"""Настройки attribution-service."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True, slots=True)
class Settings:
    """Параметры runtime-конфигурации."""

    use_inmemory: bool
    auth_jwks_url: str
    auth_jwks_json: str | None
    auth_issuer: str
    auth_audience: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            use_inmemory=os.getenv("ATTR_USE_INMEMORY", "1") == "1",
            auth_jwks_url=os.getenv(
                "ATTR_AUTH_JWKS_URL",
                "http://localhost:8000/.well-known/jwks.json",
            ),
            auth_jwks_json=os.getenv("ATTR_AUTH_JWKS_JSON"),
            auth_issuer=os.getenv("ATTR_AUTH_ISSUER", "auth_service"),
            auth_audience=os.getenv("ATTR_AUTH_AUDIENCE", "platform_clients"),
        )
