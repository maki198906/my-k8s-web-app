import random
import string

from models import Link
from sqlalchemy.orm import Session


def generate_code(length: int = 6) -> str:
    """Генерирует случайный код из букв и цифр. Например: 'aB3xZ9'"""
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))


def create_link(db: Session, original_url: str) -> Link:
    """
    Создаёт новую короткую ссылку.
    Генерирует код, проверяет уникальность (на случай коллизии),
    сохраняет в базу.
    """
    # Генерируем код до тех пор, пока не найдём уникальный
    while True:
        code = generate_code()
        if not get_link_by_code(db, code):
            break

    link = Link(code=code, original_url=str(original_url))
    db.add(link)
    db.commit()
    db.refresh(link)  # обновляем объект из БД (чтобы получить id, created_at)
    return link


def get_link_by_code(db: Session, code: str) -> Link | None:
    """Находит ссылку по коду. Возвращает None, если не найдена."""
    return db.query(Link).filter(Link.code == code).first()


def increment_hits(db: Session, link: Link) -> None:
    """Увеличивает счётчик переходов на 1."""
    link.hits += 1
    db.commit()


def get_all_links(db: Session) -> list[Link]:
    """Возвращает все ссылки (для admin-эндпоинта)."""
    return db.query(Link).order_by(Link.created_at.desc()).all()


def delete_link(db: Session, code: str) -> bool:
    """
    Удаляет ссылку по коду.
    Возвращает True если удалена, False если не найдена.
    """
    link = get_link_by_code(db, code)
    if not link:
        return False
    db.delete(link)
    db.commit()
    return True
