"""Composition root attribution-service."""

from __future__ import annotations

from dataclasses import dataclass

from src.application.facade.application_facade import ApplicationFacade
from src.application.ports.access_token_verifier import AccessTokenVerifier
from src.application.reporting.handlers.get_campaign_report_handler import (
    GetCampaignReportHandler,
)
from src.application.reporting.handlers.get_channel_report_handler import (
    GetChannelReportHandler,
)
from src.application.reporting.queries.dto import (
    GetCampaignReportQuery,
    GetChannelReportQuery,
)
from src.application.tokens.commands.dto import (
    CreateReferralTokenCommand,
    DisableReferralTokenCommand,
)
from src.application.tokens.handlers.manage_referral_tokens_handlers import (
    CreateReferralTokenHandler,
    DisableReferralTokenHandler,
    ListReferralTokensHandler,
)
from src.application.tokens.queries.dto import ListReferralTokensQuery
from src.application.tracking.commands.dto import (
    RecordPaidConversionCommand,
    RecordRequestedConversionCommand,
    TrackVisitCommand,
)
from src.application.tracking.handlers.tracking_handlers import (
    RecordPaidConversionHandler,
    RecordRequestedConversionHandler,
    ResolveDiscountHandler,
    TrackVisitHandler,
)
from src.application.tracking.queries.dto import ResolveDiscountQuery
from src.infrastructure.auth.jwks_access_token_verifier import JwksAccessTokenVerifier
from src.infrastructure.clock.system_clock import SystemClock
from src.infrastructure.config.settings import Settings
from src.infrastructure.db.inmemory.repositories import (
    InMemoryAttributionConversionRepository,
    InMemoryAttributionVisitRepository,
    InMemoryReferralTokenRepository,
)
from src.infrastructure.db.inmemory.uow import (
    InMemoryRepositoryProvider,
    InMemoryUnitOfWork,
)
from src.infrastructure.db.sqlalchemy.base import Base
from src.infrastructure.db.sqlalchemy.session import build_engine, build_session_factory
from src.infrastructure.db.sqlalchemy.uow.sqlalchemy_uow import SqlalchemyUnitOfWork
from src.infrastructure.id.uuid_generator import UuidGenerator


@dataclass(frozen=True, slots=True)
class RuntimeContainer:
    """Runtime зависимости attribution-service."""

    settings: Settings
    facade: ApplicationFacade
    access_token_verifier: AccessTokenVerifier


def build_runtime() -> RuntimeContainer:
    """Собирает граф зависимостей сервиса."""

    settings = Settings.from_env()

    access_token_verifier = JwksAccessTokenVerifier(
        issuer=settings.auth_issuer,
        audience=settings.auth_audience,
        jwks_url=settings.auth_jwks_url,
        jwks_json=settings.auth_jwks_json,
    )

    if settings.use_inmemory:
        uow = InMemoryUnitOfWork(
            InMemoryRepositoryProvider(
                referral_tokens=InMemoryReferralTokenRepository(),
                visits=InMemoryAttributionVisitRepository(),
                conversions=InMemoryAttributionConversionRepository(),
            )
        )
    else:
        from src.infrastructure.db.sqlalchemy import models as _models  # noqa: F401

        engine = build_engine(settings.database_url)
        if settings.auto_create_schema:
            Base.metadata.create_all(bind=engine)
        session_factory = build_session_factory(engine)
        uow = SqlalchemyUnitOfWork(session_factory)

    clock = SystemClock()
    id_generator = UuidGenerator()

    facade = ApplicationFacade()
    facade.register_command_handler(
        CreateReferralTokenCommand,
        CreateReferralTokenHandler(uow=uow, clock=clock, id_generator=id_generator),
    )
    facade.register_command_handler(
        DisableReferralTokenCommand,
        DisableReferralTokenHandler(uow=uow, clock=clock),
    )
    facade.register_query_handler(
        ListReferralTokensQuery, ListReferralTokensHandler(uow=uow)
    )

    facade.register_command_handler(
        TrackVisitCommand,
        TrackVisitHandler(uow=uow, clock=clock, id_generator=id_generator),
    )
    facade.register_query_handler(
        ResolveDiscountQuery, ResolveDiscountHandler(uow=uow, clock=clock)
    )
    facade.register_command_handler(
        RecordRequestedConversionCommand,
        RecordRequestedConversionHandler(uow=uow, clock=clock),
    )
    facade.register_command_handler(
        RecordPaidConversionCommand,
        RecordPaidConversionHandler(uow=uow, clock=clock),
    )

    facade.register_query_handler(
        GetChannelReportQuery, GetChannelReportHandler(uow=uow)
    )
    facade.register_query_handler(
        GetCampaignReportQuery, GetCampaignReportHandler(uow=uow)
    )
    return RuntimeContainer(
        settings=settings,
        facade=facade,
        access_token_verifier=access_token_verifier,
    )
