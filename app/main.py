from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.database import create_tables
from app.routers import auth, swipe, admin, export
import os

SECRET_KEY = os.getenv("SECRET_KEY", "filmswipe-secret-key-change-in-production")

app = FastAPI(title="FilmSwipe")

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth.router)
app.include_router(swipe.router)
app.include_router(admin.router)
app.include_router(export.router)


@app.on_event("startup")
async def startup():
    create_tables()
    _seed_admin()


def _seed_admin():
    """Create default admin user if not exists."""
    from app.database import SessionLocal, User
    from app.auth_utils import hash_password
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                password_hash=hash_password("admin123"),
                role="admin",
            )
            db.add(admin_user)
            db.commit()
            print("Default admin created: admin / admin123")
    finally:
        db.close()
