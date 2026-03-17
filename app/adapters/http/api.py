"""FastAPI application factory."""

from fastapi import FastAPI

from app.adapters.http.routers.users import router as users_router

app = FastAPI()

app.include_router(users_router)
