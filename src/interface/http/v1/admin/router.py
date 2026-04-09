"""HTTP роуты admin v1 attribution-service."""

from __future__ import annotations

from dataclasses import asdict
from datetime import date

from fastapi import APIRouter, Depends, Query

from src.application.reporting.queries.dto import GetChannelReportQuery
from src.application.tokens.commands.dto import (
    CreateReferralTokenCommand,
    DisableReferralTokenCommand,
)
from src.application.tokens.queries.dto import ListReferralTokensQuery
from src.interface.http.common.actor import HttpActor, get_http_actor
from src.interface.http.v1.schemas.reporting import (
    ChannelReportItemResponse,
    ChannelReportResponse,
)
from src.interface.http.v1.schemas.tokens import (
    CreateReferralTokenRequest,
    ReferralTokenListResponse,
    ReferralTokenResponse,
)
from src.interface.http.wiring import get_facade

router = APIRouter(prefix="/v1/admin", tags=["admin"])


@router.post("/referral-tokens", response_model=ReferralTokenResponse, status_code=201)
def create_referral_token(
    payload: CreateReferralTokenRequest,
    actor: HttpActor = Depends(get_http_actor),
    facade=Depends(get_facade),
) -> ReferralTokenResponse:
    result = facade.execute(
        CreateReferralTokenCommand(
            channel=payload.channel,
            discount_type=payload.discount_type,
            discount_value=payload.discount_value,
            course_id=payload.course_id,
            campaign=payload.campaign,
            expires_at=payload.expires_at,
            course_starts_at=payload.course_starts_at,
            actor_id=actor.actor_id,
            actor_roles=actor.roles,
        )
    )
    return ReferralTokenResponse(**asdict(result))


@router.get("/referral-tokens", response_model=ReferralTokenListResponse)
def list_referral_tokens(
    channel: str | None = Query(default=None),
    status: str | None = Query(default=None),
    actor: HttpActor = Depends(get_http_actor),
    facade=Depends(get_facade),
) -> ReferralTokenListResponse:
    result = facade.query(
        ListReferralTokensQuery(
            actor_id=actor.actor_id,
            actor_roles=actor.roles,
            channel=channel,
            status=status,
        )
    )
    return ReferralTokenListResponse(items=[ReferralTokenResponse(**asdict(item)) for item in result])


@router.post("/referral-tokens/{token}/disable", response_model=ReferralTokenResponse)
def disable_referral_token(
    token: str,
    actor: HttpActor = Depends(get_http_actor),
    facade=Depends(get_facade),
) -> ReferralTokenResponse:
    result = facade.execute(
        DisableReferralTokenCommand(
            token=token,
            actor_id=actor.actor_id,
            actor_roles=actor.roles,
        )
    )
    return ReferralTokenResponse(**asdict(result))


@router.get("/reports/channels", response_model=ChannelReportResponse)
def get_channels_report(
    date_from: date,
    date_to: date,
    actor: HttpActor = Depends(get_http_actor),
    facade=Depends(get_facade),
) -> ChannelReportResponse:
    result = facade.query(
        GetChannelReportQuery(
            date_from=date_from,
            date_to=date_to,
            actor_id=actor.actor_id,
            actor_roles=actor.roles,
        )
    )
    return ChannelReportResponse(
        items=[ChannelReportItemResponse(**asdict(item)) for item in result]
    )
