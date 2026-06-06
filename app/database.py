from sqlalchemy import create_engine, Column, Integer, String, Text, SmallInteger, TIMESTAMP, UniqueConstraint, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./filmswipe.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), nullable=False, unique=True)
    password_hash = Column(String(128), nullable=False)
    role = Column(String(16), default="user")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    likes = relationship("Like", back_populates="user", cascade="all, delete")
    dislikes = relationship("Dislike", back_populates="user", cascade="all, delete")


class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(256), nullable=False)
    genre = Column(String(64), nullable=False)
    year = Column(SmallInteger)
    description = Column(Text, nullable=True)
    poster_path = Column(String(512), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    likes = relationship("Like", back_populates="movie", cascade="all, delete")
    dislikes = relationship("Dislike", back_populates="movie", cascade="all, delete")


class Like(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("user_id", "movie_id"),)
    user = relationship("User", back_populates="likes")
    movie = relationship("Movie", back_populates="likes")


class Dislike(Base):
    __tablename__ = "dislikes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("user_id", "movie_id"),)
    user = relationship("User", back_populates="dislikes")
    movie = relationship("Movie", back_populates="dislikes")


def create_tables():
    Base.metadata.create_all(bind=engine)
