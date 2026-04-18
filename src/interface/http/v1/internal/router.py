"""HTTP роуты internal v1 attribution-service."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Depends

from src.application.tracking.commands.dto import (
    RecordPaidConversionCommand,
    RecordRequestedConversionCommand,
)
from src.application.tracking.queries.dto import ResolveDiscountQuery
from src.interface.http.common.actor import HttpActor, get_internal_http_actor
from src.interface.http.v1.schemas.tracking import (
    ConversionResponse,
    RecordPaidConversionRequest,
    RecordRequestedConversionRequest,
    ResolveDiscountRequest,
    ResolveDiscountResponse,
)
from src.interface.http.wiring import get_facade

router = APIRouter(prefix="/v1/internal", tags=["internal"])


@router.post("/discount/resolve", response_model=ResolveDiscountResponse)
def resolve_discount(
    payload: ResolveDiscountRequest,
    actor: HttpActor = Depends(get_internal_http_actor),
    facade=Depends(get_facade),
) -> ResolveDiscountResponse:
    result = facade.query(
        ResolveDiscountQuery(
            course_id=payload.course_id,
            referral_token=payload.referral_token,
            channel=payload.channel,
            parent_id=payload.parent_id,
            actor_id=actor.actor_id,
            actor_roles=actor.roles,
        )
    )
    return ResolveDiscountResponse(**asdict(result))


@router.post(
    "/conversions/requested", response_model=ConversionResponse, status_code=202
)
def record_requested_conversion(
    payload: RecordRequestedConversionRequest,
    actor: HttpActor = Depends(get_internal_http_actor),
    facade=Depends(get_facade),
) -> ConversionResponse:
    result = facade.execute(
        RecordRequestedConversionCommand(
            access_grant_id=payload.access_grant_id,
            course_id=payload.course_id,
            student_id=payload.student_id,
            parent_id=payload.parent_id,
            token=payload.token,
            channel=payload.channel,
            discount_amount=payload.discount.amount if payload.discount else None,
            discount_currency=payload.discount.currency if payload.discount else None,
            actor_id=actor.actor_id,
            actor_roles=actor.roles,
        )
    )
    return ConversionResponse(**asdict(result))


@router.post("/conversions/paid", response_model=ConversionResponse, status_code=202)
def record_paid_conversion(
    payload: RecordPaidConversionRequest,
    actor: HttpActor = Depends(get_internal_http_actor),
    facade=Depends(get_facade),
) -> ConversionResponse:
    result = facade.execute(
        RecordPaidConversionCommand(
            access_grant_id=payload.access_grant_id,
            paid_amount=payload.paid_amount.amount,
            currency=payload.paid_amount.currency,
            approved_by_admin_id=payload.approved_by_admin_id,
            actor_id=actor.actor_id,
            actor_roles=actor.roles,
        )
    )
    return ConversionResponse(**asdict(result))
