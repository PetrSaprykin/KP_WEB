import os
import uuid
from fastapi import APIRouter, Request, Form, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db, Movie
from app.auth_utils import get_current_user

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="app/templates")

UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _require_admin(request: Request, db: Session):
    user = get_current_user(request, db)
    if not user:
        raise Exception("redirect_login")
    if user.role != "admin":
        raise Exception("forbidden")
    return user


@router.get("", response_class=HTMLResponse)
async def admin_panel(request: Request, db: Session = Depends(get_db)):
    try:
        user = _require_admin(request, db)
    except Exception as e:
        if "redirect_login" in str(e):
            return RedirectResponse("/auth/login", status_code=303)
        return HTMLResponse("Доступ запрещён", status_code=403)
    movies = db.query(Movie).order_by(Movie.id).all()
    return templates.TemplateResponse(
        "admin/panel.html",
        {"request": request, "user": user, "movies": movies, "edit_movie": None},
    )


@router.get("/edit/{movie_id}", response_class=HTMLResponse)
async def edit_movie_page(movie_id: int, request: Request, db: Session = Depends(get_db)):
    try:
        user = _require_admin(request, db)
    except Exception as e:
        if "redirect_login" in str(e):
            return RedirectResponse("/auth/login", status_code=303)
        return HTMLResponse("Доступ запрещён", status_code=403)
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    movies = db.query(Movie).order_by(Movie.id).all()
    return templates.TemplateResponse(
        "admin/panel.html",
        {"request": request, "user": user, "movies": movies, "edit_movie": movie},
    )


@router.post("/add")
async def add_movie(
    request: Request,
    title: str = Form(...),
    genre: str = Form(...),
    year: int = Form(...),
    description: str = Form(""),
    poster: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    try:
        _require_admin(request, db)
    except Exception as e:
        if "redirect_login" in str(e):
            return RedirectResponse("/auth/login", status_code=303)
        return HTMLResponse("Доступ запрещён", status_code=403)

    poster_path = None
    if poster and poster.filename:
        ext = os.path.splitext(poster.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        content = await poster.read()
        with open(filepath, "wb") as f:
            f.write(content)
        poster_path = f"/static/uploads/{filename}"

    movie = Movie(title=title, genre=genre, year=year, description=description, poster_path=poster_path)
    db.add(movie)
    db.commit()
    return RedirectResponse("/admin", status_code=303)


@router.post("/edit/{movie_id}")
async def update_movie(
    movie_id: int,
    request: Request,
    title: str = Form(...),
    genre: str = Form(...),
    year: int = Form(...),
    description: str = Form(""),
    poster: UploadFile = File(None),
    db: Session = Depends(get_db),
):
    try:
        _require_admin(request, db)
    except Exception as e:
        if "redirect_login" in str(e):
            return RedirectResponse("/auth/login", status_code=303)
        return HTMLResponse("Доступ запрещён", status_code=403)

    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        return RedirectResponse("/admin", status_code=303)

    movie.title = title
    movie.genre = genre
    movie.year = year
    movie.description = description

    if poster and poster.filename:
        ext = os.path.splitext(poster.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        content = await poster.read()
        with open(filepath, "wb") as f:
            f.write(content)
        movie.poster_path = f"/static/uploads/{filename}"

    db.commit()
    return RedirectResponse("/admin", status_code=303)


@router.post("/delete/{movie_id}")
async def delete_movie(movie_id: int, request: Request, db: Session = Depends(get_db)):
    try:
        _require_admin(request, db)
    except Exception as e:
        if "redirect_login" in str(e):
            return RedirectResponse("/auth/login", status_code=303)
        return HTMLResponse("Доступ запрещён", status_code=403)

    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie:
        db.delete(movie)
        db.commit()
    return RedirectResponse("/admin", status_code=303)
