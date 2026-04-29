import socket
from contextlib import asynccontextmanager

import config
import crud
from database import create_tables, get_db
from fastapi import APIRouter, Depends, FastAPI, Header, HTTPException
from fastapi.responses import RedirectResponse
from schemas import LinkResponse, ShortenRequest, StatsResponse
from sqlalchemy.orm import Session


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
    lifespan=lifespan,
)

# Все API эндпоинты получают префикс /api
# Это один роутер — чистое разделение без дублирования кода
api = APIRouter(prefix="/api")


def verify_admin(x_admin_token: str = Header(default=None)):
    if x_admin_token != config.ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid admin token")


# ── /api/* эндпоинты ──────────────────────────────────────────────


@api.get("/health")
def health():
    return {"status": "ok"}


@api.get("/info")
def info():
    return {
        "app": config.APP_NAME,
        "version": config.APP_VERSION,
        "hostname": socket.gethostname(),
    }


@api.post("/shorten", response_model=LinkResponse)
def shorten(request: ShortenRequest, db: Session = Depends(get_db)):
    link = crud.create_link(db, str(request.url))
    # Короткая ссылка теперь с /r/ префиксом
    short_url = f"{config.BASE_URL}/r/{link.code}"
    return LinkResponse(
        code=link.code,
        short_url=short_url,
        original_url=link.original_url,
    )


@api.get("/stats/{code}", response_model=StatsResponse)
def stats(code: str, db: Session = Depends(get_db)):
    link = crud.get_link_by_code(db, code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return StatsResponse(
        code=link.code,
        original_url=link.original_url,
        hits=link.hits,
        created_at=link.created_at,
    )


@api.get("/links", dependencies=[Depends(verify_admin)])
def list_links(db: Session = Depends(get_db)):
    links = crud.get_all_links(db)
    return [
        {
            "code": link.code,
            "original_url": link.original_url,
            "hits": link.hits,
            "created_at": link.created_at,
            "short_url": f"{config.BASE_URL}/r/{link.code}",
        }
        for link in links
    ]


@api.delete("/links/{code}", dependencies=[Depends(verify_admin)])
def delete_link(code: str, db: Session = Depends(get_db)):
    deleted = crud.delete_link(db, code)
    if not deleted:
        raise HTTPException(status_code=404, detail="Link not found")
    return {"detail": f"Link '{code}' deleted"}


# Подключаем роутер к приложению
app.include_router(api)


# ── /r/{code} — редирект (НЕ под /api, отдельный маршрут) ────────


@app.get("/r/{code}")
def redirect(code: str, db: Session = Depends(get_db)):
    link = crud.get_link_by_code(db, code)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    crud.increment_hits(db, link)
    return RedirectResponse(url=link.original_url, status_code=307)
