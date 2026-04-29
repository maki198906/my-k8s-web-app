from datetime import datetime

from pydantic import BaseModel, HttpUrl


class ShortenRequest(BaseModel):
    """
    Тело POST-запроса на /shorten.
    Pydantic автоматически валидирует: если url не является
    корректным HTTP/HTTPS адресом — вернёт ошибку 422.
    """

    url: HttpUrl


class LinkResponse(BaseModel):
    """
    Ответ при создании ссылки.
    short_url — это полный адрес: http://kubernetes.docker.internal/aB3xZ9
    """

    code: str
    short_url: str
    original_url: str


class StatsResponse(BaseModel):
    """
    Ответ на запрос статистики по коду.
    """

    code: str
    original_url: str
    hits: int
    created_at: datetime
