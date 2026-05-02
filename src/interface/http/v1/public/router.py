"""HTTP роуты public attribution-service."""

from __future__ import annotations

from dataclasses import asdict
from urllib.parse import urlparse

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse

from src.application.tracking.commands.dto import TrackVisitCommand
from src.interface.http.v1.schemas.tracking import TrackClickRequest, TrackClickResponse
from src.interface.http.wiring import get_facade

router = APIRouter(prefix="/v1/public", tags=["public"])
redirect_router = APIRouter(tags=["public"])


def _is_safe_redirect_target(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _track_click(
    *,
    token: str,
    anonymous_id: str | None,
    parent_id: str | None,
    source_url: str | None,
    facade,
) -> TrackClickResponse:
    result = facade.execute(
        TrackVisitCommand(
            token=token,
            anonymous_id=anonymous_id,
            parent_id=parent_id,
            source_url=source_url,
        )
    )
    return TrackClickResponse(**asdict(result))


@router.post(
    "/referrals/{token}/click", response_model=TrackClickResponse, status_code=202
)
def track_referral_click(
    token: str,
    payload: TrackClickRequest | None = Body(default=None),
    facade=Depends(get_facade),
) -> TrackClickResponse:
    body = payload or TrackClickRequest()
    return _track_click(
        token=token,
        anonymous_id=body.anonymous_id,
        parent_id=body.parent_id,
        source_url=body.source_url,
        facade=facade,
    )


@redirect_router.get("/r/{token}", include_in_schema=False, response_model=None)
def redirect_referral_click(
    token: str,
    redirect_to: str | None = Query(default=None),
    anonymous_id: str | None = Query(default=None),
    parent_id: str | None = Query(default=None),
    source_url: str | None = Query(default=None),
    facade=Depends(get_facade),
):
    _track_click(
        token=token,
        anonymous_id=anonymous_id,
        parent_id=parent_id,
        source_url=source_url,
        facade=facade,
    )

    if redirect_to is None:
        return TrackClickResponse(accepted=True)
    if not _is_safe_redirect_target(redirect_to):
        raise HTTPException(
            status_code=400, detail="redirect_to должен быть абсолютным http/https URL."
        )
    return RedirectResponse(url=redirect_to, status_code=307)
