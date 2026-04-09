"""Фасад application-слоя attribution-service."""

from __future__ import annotations

from typing import Any, Callable


class ApplicationFacade:
    """Единая точка запуска command/query handlers."""

    def __init__(self) -> None:
        self._command_handlers: dict[type, Callable[[Any], Any]] = {}
        self._query_handlers: dict[type, Callable[[Any], Any]] = {}

    def register_command_handler(self, command_type: type, handler: Callable[[Any], Any]) -> None:
        self._command_handlers[command_type] = handler

    def register_query_handler(self, query_type: type, handler: Callable[[Any], Any]) -> None:
        self._query_handlers[query_type] = handler

    def execute(self, command: Any) -> Any:
        handler = self._command_handlers.get(type(command))
        if handler is None:
            raise LookupError(f"Handler не найден для command: {type(command).__name__}")
        return handler(command)

    def query(self, query: Any) -> Any:
        handler = self._query_handlers.get(type(query))
        if handler is None:
            raise LookupError(f"Handler не найден для query: {type(query).__name__}")
        return handler(query)
