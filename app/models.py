from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from database import Base


class Link(Base):
    """
    Таблица 'links' в SQLite.
    Каждая строка — одна сокращённая ссылка.
    """

    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    # Короткий код: например, "aB3xZ9"
    code = Column(String, unique=True, index=True, nullable=False)
    # Оригинальный URL: "https://very-long-url.com/..."
    original_url = Column(String, nullable=False)
    # Счётчик переходов. Начинается с 0.
    hits = Column(Integer, default=0, nullable=False)
    # Время создания ссылки.
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
