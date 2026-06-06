from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import os

from app.database import get_db, Movie, Like
from app.auth_utils import get_current_user

router = APIRouter()

FONT_NAME = "Helvetica"


@router.get("/export/pdf")
async def export_likes_pdf(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        from fastapi.responses import RedirectResponse
        return RedirectResponse("/auth/login", status_code=303)

    liked_movies = (
        db.query(Movie)
        .join(Like, Like.movie_id == Movie.id)
        .filter(Like.user_id == user.id)
        .all()
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("title", fontName=FONT_NAME, fontSize=18, spaceAfter=12, textColor=colors.HexColor("#1a1a2e"))
    subtitle_style = ParagraphStyle("subtitle", fontName=FONT_NAME, fontSize=11, textColor=colors.grey, spaceAfter=20)
    cell_style = ParagraphStyle("cell", fontName=FONT_NAME, fontSize=10)

    story = []
    story.append(Paragraph("FilmSwipe", title_style))
    story.append(Paragraph(f"Понравившиеся фильмы пользователя: {user.username}", subtitle_style))
    story.append(Spacer(1, 0.3*cm))

    if not liked_movies:
        story.append(Paragraph("Нет понравившихся фильмов.", cell_style))
    else:
        headers = ["#", "Название", "Жанр", "Год", "Описание"]
        data = [headers]
        for i, m in enumerate(liked_movies, 1):
            desc = (m.description or "")[:80] + ("..." if m.description and len(m.description) > 80 else "")
            data.append([
                str(i),
                Paragraph(m.title, cell_style),
                m.genre,
                str(m.year) if m.year else "—",
                Paragraph(desc, cell_style),
            ])

        col_widths = [1*cm, 5*cm, 3*cm, 1.5*cm, 7*cm]
        table = Table(data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
            ("FONTSIZE", (0, 0), (-1, 0), 11),
            ("FONTSIZE", (0, 1), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f0")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        story.append(table)

    doc.build(story)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=filmswipe_likes.pdf"},
    )
