from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:////data/shortener.db"


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def create_tables():
    """Создаёт все таблицы в базе, если их ещё нет."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Генератор сессий для FastAPI (Dependency Injection).
    FastAPI вызывает эту функцию перед каждым запросом,
    передаёт сессию в эндпоинт, и закрывает её после ответа.
    Конструкция try/finally гарантирует закрытие даже при ошибке.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
