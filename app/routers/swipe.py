from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db, Movie, Like, Dislike
from app.auth_utils import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def _get_next_movie(user_id: int, db: Session):
    liked_ids = db.query(Like.movie_id).filter(Like.user_id == user_id).subquery()
    disliked_ids = db.query(Dislike.movie_id).filter(Dislike.user_id == user_id).subquery()
    movie = (
        db.query(Movie)
        .filter(Movie.id.not_in(liked_ids))
        .filter(Movie.id.not_in(disliked_ids))
        .order_by(Movie.id)
        .first()
    )
    return movie


@router.get("/", response_class=HTMLResponse)
async def index(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/auth/login", status_code=303)
    movie = _get_next_movie(user.id, db)
    total = db.query(Movie).count()
    liked = db.query(Like).filter(Like.user_id == user.id).count()
    disliked = db.query(Dislike).filter(Dislike.user_id == user.id).count()
    return templates.TemplateResponse(
        "user/index.html",
        {"request": request, "user": user, "movie": movie, "total": total, "liked": liked, "disliked": disliked},
    )


@router.post("/swipe")
async def swipe(
    request: Request,
    movie_id: int = Form(...),
    direction: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    if direction == "like":
        existing = db.query(Like).filter_by(user_id=user.id, movie_id=movie_id).first()
        if not existing:
            db.add(Like(user_id=user.id, movie_id=movie_id))
            db.commit()
    else:
        existing = db.query(Dislike).filter_by(user_id=user.id, movie_id=movie_id).first()
        if not existing:
            db.add(Dislike(user_id=user.id, movie_id=movie_id))
            db.commit()
    return JSONResponse({"ok": True})


@router.get("/likes", response_class=HTMLResponse)
async def likes_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/auth/login", status_code=303)
    liked_movies = (
        db.query(Movie)
        .join(Like, Like.movie_id == Movie.id)
        .filter(Like.user_id == user.id)
        .all()
    )
    return templates.TemplateResponse(
        "user/likes.html",
        {"request": request, "user": user, "movies": liked_movies},
    )


@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse("/auth/login", status_code=303)
    liked = db.query(Like).filter(Like.user_id == user.id).count()
    disliked = db.query(Dislike).filter(Dislike.user_id == user.id).count()
    return templates.TemplateResponse(
        "user/profile.html",
        {"request": request, "user": user, "liked": liked, "disliked": disliked, "total": liked + disliked},
    )
