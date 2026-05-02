"""HTTP роуты admin v1 attribution-service."""

from __future__ import annotations

import csv
from dataclasses import asdict
from datetime import date
from io import StringIO

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from src.application.reporting.queries.dto import (
    GetCampaignReportQuery,
    GetChannelReportQuery,
)
from src.application.tokens.commands.dto import (
    CreateReferralTokenCommand,
    DisableReferralTokenCommand,
)
from src.application.tokens.queries.dto import ListReferralTokensQuery
from src.interface.http.common.actor import HttpActor, get_http_actor
from src.interface.http.v1.schemas.reporting import (
    CampaignReportItemResponse,
    CampaignReportResponse,
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
            source=payload.source,
            medium=payload.medium,
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
    return ReferralTokenListResponse(
        items=[ReferralTokenResponse(**asdict(item)) for item in result]
    )


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


@router.get("/campaigns/stats", response_model=CampaignReportResponse)
def get_campaigns_report(
    date_from: date,
    date_to: date,
    channel: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    actor: HttpActor = Depends(get_http_actor),
    facade=Depends(get_facade),
) -> CampaignReportResponse:
    result = facade.query(
        GetCampaignReportQuery(
            date_from=date_from,
            date_to=date_to,
            channel=channel,
            limit=limit,
            offset=offset,
            actor_id=actor.actor_id,
            actor_roles=actor.roles,
        )
    )
    return CampaignReportResponse(
        items=[CampaignReportItemResponse(**asdict(item)) for item in result.items],
        limit=result.limit,
        offset=result.offset,
        total=result.total,
    )


@router.get("/campaigns/stats.csv", response_class=Response)
def export_campaigns_report_csv(
    date_from: date,
    date_to: date,
    channel: str | None = Query(default=None),
    actor: HttpActor = Depends(get_http_actor),
    facade=Depends(get_facade),
) -> Response:
    result = facade.query(
        GetCampaignReportQuery(
            date_from=date_from,
            date_to=date_to,
            channel=channel,
            limit=10_000,
            offset=0,
            actor_id=actor.actor_id,
            actor_roles=actor.roles,
        )
    )

    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "channel",
            "campaign",
            "clicks",
            "requested",
            "paid",
            "gross_revenue_amount",
            "gross_revenue_currency",
            "discount_total_amount",
            "discount_total_currency",
        ]
    )
    for item in result.items:
        writer.writerow(
            [
                item.channel,
                item.campaign or "",
                item.clicks,
                item.requested,
                item.paid,
                item.gross_revenue.amount,
                item.gross_revenue.currency,
                item.discount_total.amount,
                item.discount_total.currency,
            ]
        )

    return Response(
        content=buffer.getvalue(),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="campaign-stats.csv"'},
    )
