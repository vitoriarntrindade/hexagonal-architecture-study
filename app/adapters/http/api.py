"""FastAPI application factory."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.adapters.http.routers.users import router as users_router
from app.domain.exceptions import UserNotFoundError, EmailAlreadyRegisteredError

import uuid
from typing import Any


def _exception_code(exc: Exception) -> str:
	"""Convert exception class name to a snake_case error code.

	Example: UserNotFoundError -> user_not_found
	"""
	name = exc.__class__.__name__
	# Remove trailing 'Error' and convert CamelCase to snake_case
	if name.endswith("Error"):
		name = name[:-5]
	# simple CamelCase to snake_case
	snake = ""
	for i, ch in enumerate(name):
		if ch.isupper() and i:
			snake += "_"
		snake += ch.lower()
	return snake


def _error_response(exc: Exception, status_code: int, trace_id: str | None = None) -> JSONResponse:
	payload: dict[str, Any] = {"detail": str(exc), "code": _exception_code(exc)}
	if trace_id:
		payload["trace_id"] = trace_id
	return JSONResponse(status_code=status_code, content=payload)


class _TraceMiddleware(BaseHTTPMiddleware):
	async def dispatch(self, request: Request, call_next):
		trace_id = str(uuid.uuid4())
		# expose to handlers
		request.state.trace_id = trace_id
		response = await call_next(request)
		# ensure trace header on every response
		response.headers["X-Trace-Id"] = trace_id
		return response


def create_app() -> FastAPI:
	"""Factory para instanciar o FastAPI com routers, middleware and handlers."""
	app = FastAPI()

	# request tracing middleware
	app.add_middleware(_TraceMiddleware)

	# Domain error handlers: map domain exceptions to clean HTTP responses
	@app.exception_handler(UserNotFoundError)
	async def _handle_not_found(request: Request, exc: UserNotFoundError) -> JSONResponse:  # noqa: D401
		return _error_response(exc, status_code=404, trace_id=getattr(request.state, "trace_id", None))

	@app.exception_handler(EmailAlreadyRegisteredError)
	async def _handle_already_registered(request: Request, exc: EmailAlreadyRegisteredError) -> JSONResponse:  # noqa: D401
		return _error_response(exc, status_code=400, trace_id=getattr(request.state, "trace_id", None))

	app.include_router(users_router)
	return app


# Convenience exported application instance so tools like `uvicorn` can
# import the object directly without using the ``--factory`` flag.
# Keep the factory for code that prefers building the app programmatically.
app = create_app()
