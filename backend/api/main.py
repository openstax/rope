from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from .routers import admin, moodle, session, user
from rope.api import settings


app = FastAPI(title="ROPE API", root_path="/api")

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
    https_only=True,
    session_cookie="ROPE.session",
    max_age=60 * 60,  # 1 hour
)


app.include_router(user.router)
app.include_router(session.router)
app.include_router(admin.router)
app.include_router(moodle.router)
