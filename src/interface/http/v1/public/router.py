"""HTTP роуты public v1 attribution-service."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, Body, Depends

from src.application.tracking.commands.dto import TrackVisitCommand
from src.interface.http.v1.schemas.tracking import TrackClickRequest, TrackClickResponse
from src.interface.http.wiring import get_facade

router = APIRouter(prefix="/v1/public", tags=["public"])


@router.post("/referrals/{token}/click", response_model=TrackClickResponse, status_code=202)
def track_referral_click(
    token: str,
    payload: TrackClickRequest | None = Body(default=None),
    facade=Depends(get_facade),
) -> TrackClickResponse:
    body = payload or TrackClickRequest()
    result = facade.execute(
        TrackVisitCommand(
            token=token,
            anonymous_id=body.anonymous_id,
            parent_id=body.parent_id,
            source_url=body.source_url,
        )
    )
    return TrackClickResponse(**asdict(result))
