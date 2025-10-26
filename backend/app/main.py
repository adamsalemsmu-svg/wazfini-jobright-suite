from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.orm import Session

from .api.deps import get_current_user, require_db
from .api.routes_auth import router as auth_router
from .api.routes_health import router as health_router
from .core.cache import close_redis
from .core.config import settings
from .core.logging import configure_logging
from .middleware import RequestContextMiddleware
from .models import Application, User
from .schemas import ApplicationOut, UserOut

configure_logging()

openapi_tags = [
	{"name": "Auth", "description": "Authentication and session management"},
	{"name": "Users", "description": "Profile and account endpoints"},
	{"name": "Applications", "description": "User job applications"},
	{"name": "Health", "description": "Health and readiness probes"},
]

app = FastAPI(
	title="Wazifni JobRight Suite API",
	version="1.0.0",
	openapi_tags=openapi_tags,
)

if settings.cors_origins:
	app.add_middleware(
		CORSMiddleware,
		allow_origins=settings.cors_origins,
		allow_credentials=True,
		allow_methods=["*"],
		allow_headers=["*"],
	)

app.add_middleware(RequestContextMiddleware)

app.include_router(health_router)
app.include_router(auth_router)


@app.get("/users/me", response_model=UserOut, tags=["Users"])
async def read_current_user(current_user: User = Depends(get_current_user)) -> User:
	return current_user


@app.get("/applications", response_model=list[ApplicationOut], tags=["Applications"])
async def list_applications(
	current_user: User = Depends(get_current_user),
	db: Session = Depends(require_db),
) -> list[Application]:
	return db.scalars(select(Application).where(Application.user_id == current_user.id)).all()


@app.on_event("shutdown")
async def shutdown_event() -> None:
	await close_redis()
