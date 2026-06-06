"""
Seed demo data for FilmSwipe.
Run: python seed.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import create_tables, SessionLocal, Movie, User
from app.auth_utils import hash_password

MOVIES = [
    {"title": "Побег из Шоушенка", "genre": "Драма", "year": 1994,
     "description": "Банкир Энди Дюфресн осуждён за убийство жены и её любовника. В тюрьме Шоушенк он находит неожиданного друга и не теряет надежду на свободу."},
    {"title": "Зелёная миля", "genre": "Драма", "year": 1999,
     "description": "Надзиратель блока смертников обнаруживает, что один из заключённых обладает сверхъестественным даром исцеления."},
    {"title": "Начало", "genre": "Фантастика", "year": 2010,
     "description": "Вор, специализирующийся на краже корпоративных секретов с помощью технологии внедрения в сны, получает задание обратного свойства — внедрить идею."},
    {"title": "Интерстеллар", "genre": "Фантастика", "year": 2014,
     "description": "Команда астронавтов отправляется сквозь червоточину в поисках нового дома для человечества."},
    {"title": "Матрица", "genre": "Фантастика", "year": 1999,
     "description": "Хакер Нео узнаёт, что реальность, в которой он живёт, — это симуляция, а люди порабощены машинами."},
    {"title": "Оппенгеймер", "genre": "Драма", "year": 2023,
     "description": "Биография физика Роберта Оппенгеймера, руководившего Манхэттенским проектом — созданием первой ядерной бомбы."},
    {"title": "Дюна", "genre": "Фантастика", "year": 2021,
     "description": "Юный Пол Атрейдес прибывает на опасную пустынную планету Арракис, где хранится ценнейший ресурс галактики — пряность."},
    {"title": "Форрест Гамп", "genre": "Драма", "year": 1994,
     "description": "История простодушного, но доброго человека, чья жизнь пересекается с ключевыми событиями американской истории."},
    {"title": "Бойцовский клуб", "genre": "Триллер", "year": 1999,
     "description": "Офисный работник и мыльный торговец основывают подпольный бойцовский клуб, который превращается в нечто большее."},
    {"title": "1+1", "genre": "Комедия", "year": 2011,
     "description": "Богатый аристократ-тетраплегик нанимает в сиделки жизнерадостного парня из парижских трущоб. Невероятная дружба меняет обоих."},
]


def seed():
    create_tables()
    db = SessionLocal()
    try:
        # Ensure admin exists
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(username="admin", password_hash=hash_password("admin123"), role="admin")
            db.add(admin)
            db.commit()
            print("✅ Admin created: admin / admin123")

        # Add movies if catalogue is empty
        count = db.query(Movie).count()
        if count == 0:
            for m in MOVIES:
                db.add(Movie(**m))
            db.commit()
            print(f"✅ Added {len(MOVIES)} demo movies")
        else:
            print(f"ℹ️  Catalogue already has {count} movies, skipping seed")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
    print("✅ Seed complete. Run: uvicorn app.main:app --reload")
