"""FastAPI application factory."""

from fastapi import FastAPI

from app.adapters.http.routers.users import router as users_router


def create_app() -> FastAPI:
	"""Factory para instanciar o FastAPI com routers."""
	app = FastAPI()
	app.include_router(users_router)
	return app


# Convenience exported application instance so tools like `uvicorn` can
# import the object directly without using the ``--factory`` flag.
# Keep the factory for code that prefers building the app programmatically.
app = create_app()
