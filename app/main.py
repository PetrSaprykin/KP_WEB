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
    _seed_db()


def _seed_db():
    from app.database import SessionLocal, User, Movie
    from app.auth_utils import hash_password
    db = SessionLocal()
    try:
        if not db.query(User).filter(User.username == "admin").first():
            db.add(User(
                username="admin",
                password_hash=hash_password("admin123"),
                role="admin",
            ))
            db.commit()

        if db.query(Movie).count() == 0:
            movies = [
                Movie(title="Побег из Шоушенка", genre="Драма", year=1994, description="Банкир Энди Дюфресн осуждён за убийство жены. В тюрьме Шоушенк он находит друга и не теряет надежду на свободу."),
                Movie(title="Зелёная миля", genre="Драма", year=1999, description="Надзиратель блока смертников обнаруживает, что один из заключённых обладает сверхъестественным даром исцеления."),
                Movie(title="Начало", genre="Фантастика", year=2010, description="Вор, специализирующийся на краже корпоративных секретов с помощью технологии внедрения в сны."),
                Movie(title="Интерстеллар", genre="Фантастика", year=2014, description="Команда астронавтов отправляется сквозь червоточину в поисках нового дома для человечества."),
                Movie(title="Матрица", genre="Фантастика", year=1999, description="Хакер Нео узнаёт, что реальность — симуляция, а люди порабощены машинами."),
                Movie(title="Оппенгеймер", genre="Драма", year=2023, description="Биография физика Оппенгеймера, руководившего созданием первой ядерной бомбы."),
                Movie(title="Дюна", genre="Фантастика", year=2021, description="Юный Пол Атрейдес прибывает на опасную пустынную планету Арракис."),
                Movie(title="Форрест Гамп", genre="Драма", year=1994, description="История простодушного человека, чья жизнь пересекается с ключевыми событиями американской истории."),
                Movie(title="Бойцовский клуб", genre="Триллер", year=1999, description="Офисный работник и мыльный торговец основывают подпольный бойцовский клуб, который превращается в нечто большее."),
                Movie(title="1+1", genre="Комедия", year=2011, description="Богатый аристократ нанимает в сиделки парня из трущоб. Невероятная дружба меняет обоих."),
                Movie(title="Властелин колец: Братство кольца", genre="Фэнтези", year=2001, description="Хоббит Фродо получает Кольцо Всевластья и отправляется в опасное путешествие, чтобы уничтожить его в огне Роковой горы."),
                Movie(title="Властелин колец: Две крепости", genre="Фэнтези", year=2002, description="Братство распалось. Фродо и Сэм продолжают путь к Мордору, а их друзья сражаются у стен крепости Хельмова Падь."),
                Movie(title="Властелин колец: Возвращение короля", genre="Фэнтези", year=2003, description="Финальная битва за Средиземье. Арагорн ведёт войска к вратам Мордора, пока Фродо добирается до Роковой горы."),
                Movie(title="Гладиатор", genre="Боевик", year=2000, description="Римский полководец Максимус предан и лишён всего. Став гладиатором, он жаждет мести императору."),
                Movie(title="Тёмный рыцарь", genre="Боевик", year=2008, description="Бэтмен противостоит Джокеру — хаотичному преступному гению, который хочет погрузить Готэм в анархию."),
                Movie(title="Список Шиндлера", genre="Драма", year=1993, description="Немецкий предприниматель Оскар Шиндлер спасает более тысячи евреев во время Холокоста."),
                Movie(title="Криминальное чтиво", genre="Криминал", year=1994, description="Переплетающиеся истории криминального мира Лос-Анджелеса, рассказанные в нелинейном стиле."),
                Movie(title="Леон", genre="Триллер", year=1994, description="Профессиональный киллер берёт под опеку девочку, чья семья была убита продажными полицейскими."),
                Movie(title="Семь", genre="Триллер", year=1995, description="Два детектива охотятся за серийным убийцей, использующим семь смертных грехов как мотив преступлений."),
                Movie(title="Молчание ягнят", genre="Триллер", year=1991, description="Агент ФБР вынуждена обратиться за помощью к заключённому психиатру-каннибалу Ганнибалу Лектеру."),
                Movie(title="Назад в будущее", genre="Фантастика", year=1985, description="Подросток Марти МакФлай случайно попадает в 1955 год на машине времени и должен вернуться в своё время."),
                Movie(title="Терминатор 2: Судный день", genre="Боевик", year=1991, description="Терминатор T-800 возвращается из будущего, чтобы защитить Джона Коннора от более совершенного робота T-1000."),
                Movie(title="Аватар", genre="Фантастика", year=2009, description="Парализованный морпех отправляется на планету Пандора, где вступает в конфликт между людьми и местными жителями — на'ви."),
                Movie(title="Титаник", genre="Мелодрама", year=1997, description="История любви бедного художника и богатой девушки на борту обречённого лайнера."),
                Movie(title="Храброе сердце", genre="Боевик", year=1995, description="Шотландский воин Уильям Уоллес поднимает восстание против английского владычества в XIII веке."),
                Movie(title="Пираты Карибского моря", genre="Приключения", year=2003, description="Эксцентричный пират Джек Воробей помогает молодому кузнецу спасти возлюбленную из лап пиратов."),
                Movie(title="Индиана Джонс: В поисках утраченного ковчега", genre="Приключения", year=1981, description="Профессор археологии Индиана Джонс охотится за Ковчегом Завета, соревнуясь с нацистами."),
                Movie(title="Джокер", genre="Триллер", year=2019, description="История превращения неудачливого комика Артура Флека в культового злодея Готэма — Джокера."),
                Movie(title="Паразиты", genre="Триллер", year=2019, description="Бедная корейская семья постепенно внедряется в жизнь богатого семейства с непредсказуемыми последствиями."),
                Movie(title="Достучаться до небес", genre="Драма", year=1997, description="Два смертельно больных пациента сбегают из больницы, чтобы увидеть море, угоняют машину мафии и пускаются в авантюру."),
            ]
            db.add_all(movies)
            db.commit()
    finally:
        db.close()