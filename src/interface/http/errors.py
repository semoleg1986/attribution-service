"""HTTP обработчики ошибок attribution-service."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.domain.errors import AccessDeniedError, InvariantViolationError, NotFoundError
from src.interface.http.problem_types import (
    PROBLEM_ACCESS_DENIED,
    PROBLEM_CONFLICT,
    PROBLEM_INTERNAL,
    PROBLEM_NOT_FOUND,
    PROBLEM_VALIDATION,
)


def _problem(
    *,
    status_code: int,
    problem_type: str,
    title: str,
    detail: str,
    request: Request,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        media_type="application/problem+json",
        content={
            "type": problem_type,
            "title": title,
            "status": status_code,
            "detail": detail,
            "instance": request.url.path,
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрирует transport mapping доменных ошибок."""

    @app.exception_handler(InvariantViolationError)
    async def handle_invariant(request: Request, exc: InvariantViolationError) -> JSONResponse:
        return _problem(
            status_code=409,
            problem_type=PROBLEM_CONFLICT,
            title="Нарушение инварианта",
            detail=str(exc),
            request=request,
        )

    @app.exception_handler(AccessDeniedError)
    async def handle_access_denied(request: Request, exc: AccessDeniedError) -> JSONResponse:
        return _problem(
            status_code=403,
            problem_type=PROBLEM_ACCESS_DENIED,
            title="Доступ запрещен",
            detail=str(exc),
            request=request,
        )

    @app.exception_handler(NotFoundError)
    async def handle_not_found(request: Request, exc: NotFoundError) -> JSONResponse:
        return _problem(
            status_code=404,
            problem_type=PROBLEM_NOT_FOUND,
            title="Не найдено",
            detail=str(exc),
            request=request,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _problem(
            status_code=422,
            problem_type=PROBLEM_VALIDATION,
            title="Ошибка валидации",
            detail=str(exc),
            request=request,
        )

    @app.exception_handler(ValueError)
    async def handle_value_error(request: Request, exc: ValueError) -> JSONResponse:
        return _problem(
            status_code=422,
            problem_type=PROBLEM_VALIDATION,
            title="Ошибка валидации",
            detail=str(exc),
            request=request,
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, _exc: Exception) -> JSONResponse:
        return _problem(
            status_code=500,
            problem_type=PROBLEM_INTERNAL,
            title="Внутренняя ошибка",
            detail="Неожиданная ошибка сервиса.",
            request=request,
        )
