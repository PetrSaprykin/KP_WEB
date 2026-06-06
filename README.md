# FilmSwipe 🎬

Веб-приложение для подбора фильмов с механикой свайпа.

**Стек:** FastAPI · SQLAlchemy · SQLite/PostgreSQL · Bootstrap 5.3 · Jinja2

---

## Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Инициализация БД и демо-данных

```bash
python seed.py
```

Создаётся:
- База данных `filmswipe.db` (SQLite)
- Аккаунт администратора: **admin / admin123**
- 10 демо-фильмов в каталоге

### 3. Запуск

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Откройте [http://localhost:8000](http://localhost:8000)

---

## Структура проекта

```
filmswipe/
├── app/
│   ├── main.py              # FastAPI приложение
│   ├── database.py          # Модели SQLAlchemy (User, Movie, Like, Dislike)
│   ├── auth_utils.py        # Хэширование паролей, проверка сессий
│   ├── routers/
│   │   ├── auth.py          # Регистрация / вход / выход
│   │   ├── swipe.py         # Главная страница, свайп, лайки, профиль
│   │   ├── admin.py         # CRUD-панель администратора
│   │   └── export.py        # Экспорт понравившихся фильмов в PDF
│   ├── templates/
│   │   ├── base.html        # Базовый шаблон с навбаром
│   │   ├── auth/            # login.html, register.html
│   │   ├── user/            # index.html, likes.html, profile.html
│   │   └── admin/           # panel.html
│   └── static/
│       ├── css/main.css     # Стили (тёмная тема)
│       ├── js/swipe.js      # Механика свайпа (Touch + Mouse + клавиши)
│       └── uploads/         # Загруженные постеры
├── seed.py                  # Скрипт начального заполнения БД
├── requirements.txt
└── README.md
```

---

## Аккаунты

| Роль | Логин | Пароль |
|------|-------|--------|
| Администратор | `admin` | `admin123` |
| Пользователь | регистрация на `/auth/register` | по выбору |

---

## Функциональность

### Пользователь
- Регистрация и вход с сессионными куки
- Свайп карточек фильмов (мышь, тач, клавиши ← →)
- Лайк (вправо) / Дизлайк (влево) без повтора уже оценённых
- Страница понравившихся фильмов с модальным окном деталей
- Экспорт понравившихся в PDF
- Страница профиля со статистикой

### Администратор
- CRUD-панель для управления каталогом фильмов
- Загрузка постеров (изображения хранятся в `app/static/uploads/`)
- Все изменения мгновенно отображаются для всех пользователей

---

## Переменные окружения

| Переменная | По умолчанию | Описание |
|-----------|-------------|---------|
| `DATABASE_URL` | `sqlite:///./filmswipe.db` | URL базы данных |
| `SECRET_KEY` | `filmswipe-secret-key-change-in-production` | Ключ подписи сессий |

### Пример с PostgreSQL

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/filmswipe"
export SECRET_KEY="your-secret-key-here"
python seed.py
uvicorn app.main:app --reload
```

---

## Модель данных

```
User(id, username, password_hash, role, created_at)
  ├── Like(id, user_id→User, movie_id→Movie, created_at)
  └── Dislike(id, user_id→User, movie_id→Movie, created_at)

Movie(id, title, genre, year, description, poster_path, created_at)
  ├── Like(...)
  └── Dislike(...)
```

Ограничение `UNIQUE(user_id, movie_id)` в таблицах Like и Dislike исключает повторную оценку одного фильма.

---

## Инструкции для Claude Code

Если нужно доработать или расширить приложение через Claude Code:

1. **Добавить поле к фильму** — изменить модель в `app/database.py`, шаблон `admin/panel.html` и роутер `app/routers/admin.py`
2. **Изменить алгоритм подбора** — функция `_get_next_movie()` в `app/routers/swipe.py`
3. **Изменить стили** — `app/static/css/main.css` (CSS-переменные в `:root`)
4. **Механика свайпа** — `app/static/js/swipe.js`
5. **PDF-экспорт** — `app/routers/export.py` (используется ReportLab)

После изменений моделей БД пересоздайте таблицы:
```bash
python -c "from app.database import create_tables; create_tables()"
```
