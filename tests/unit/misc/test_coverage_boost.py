from __future__ import annotations

import importlib
from datetime import UTC, datetime

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.application.facade.application_facade import ApplicationFacade
from src.domain.conversions.conversion.policies import InternalPolicy
from src.domain.errors import AccessDeniedError, InvariantViolationError
from src.domain.shared.entity import EntityMeta
from src.domain.shared.value_objects import Money
from src.domain.tokens.referral_token.policies import ActorContext
from src.interface.http.common.actor import get_http_actor
from src.interface.http.errors import register_exception_handlers


def test_main_module_entrypoint_importable() -> None:
    module = importlib.import_module("src.interface.http.main")
    assert module.app is not None


def test_facade_missing_execute_handler_branch() -> None:
    facade = ApplicationFacade()

    class UnknownCommand:
        pass

    with pytest.raises(LookupError):
        facade.execute(UnknownCommand())


def test_entity_meta_and_money_and_internal_policy_branches() -> None:
    now = datetime(2026, 4, 9, tzinfo=UTC)
    meta = EntityMeta.create(at=now, actor_id="u-1")
    meta.mark_archived(at=now, actor_id="u-2")
    assert meta.archived_by == "u-2"

    with pytest.raises(InvariantViolationError):
        Money(amount=-1, currency="USD")
    with pytest.raises(InvariantViolationError):
        Money(amount=1, currency="US")

    with pytest.raises(AccessDeniedError):
        InternalPolicy.ensure_can_call_internal(
            ActorContext(actor_id="u-1", roles={"parent"})
        )


def test_http_actor_and_error_handlers_additional_branches() -> None:
    with pytest.raises(Exception):
        get_http_actor(authorization="Bearer   ", verifier=object())

    class _Verifier:
        def decode_access(self, _: str) -> dict[str, str]:
            return {"sub": "u-1", "roles": "not-list"}

    with pytest.raises(Exception):
        get_http_actor(authorization="Bearer token", verifier=_Verifier())

    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/value")
    def value() -> None:
        raise ValueError("bad")

    @app.get("/boom")
    def boom() -> None:
        raise RuntimeError("boom")

    client = TestClient(app, raise_server_exceptions=False)
    assert client.get("/value").status_code == 422
    assert client.get("/boom").status_code == 500
