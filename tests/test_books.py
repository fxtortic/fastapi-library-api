"""
Тести за патерном з документації FastAPI (TestClient, sync def test_...).
SQLite in-memory — нуль зовнішніх залежностей (ні Docker, ні Postgres).

pip install httpx aiosqlite pytest
"""

import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app

# ── SQLite in-memory через aiosqlite (сумісно з async додатком) ──

engine = create_async_engine(
    "sqlite+aiosqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # одне з'єднання — інакше in-memory БД зникне
)
TestingSessionLocal = async_sessionmaker(
    bind=engine, autocommit=False, autoflush=False, expire_on_commit=False,
)


async def override_get_db():
    """async — бо ваш додаток очікує AsyncSession."""
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


# ── Фікстура: чиста БД перед кожним тестом ──


def _run(coro):
    """Хелпер: запустити async у sync-фікстурі."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@pytest.fixture(autouse=True)
def setup_db():
    async def _create():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def _drop():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    _run(_create())
    yield
    _run(_drop())


# ── Клієнт — точно як у документації FastAPI ──

client = TestClient(app)


# ─────────────── ТЕСТИ ───────────────
# Звичайні def, без async/await — як рекомендує docs.


def test_create_book():
    response = client.post("/books/", json={
        "title": "Test Book",
        "author": "Author",
        "description": "Description",
        "status": "available",
        "year": 2024,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Book"
    assert "id" in data


def test_get_books_pagination():
    for i in range(5):
        client.post("/books/", json={
            "title": f"Book {i}",
            "author": "Author",
            "description": "Desc",
            "status": "available",
            "year": 2020 + i,
        })

    response = client.get("/books/?limit=2&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["limit"] == 2
    assert data["offset"] == 0

    response2 = client.get("/books/?limit=2&offset=2")
    data2 = response2.json()
    assert len(data2["items"]) == 2
    assert data2["offset"] == 2


def test_get_book_by_id():
    create_resp = client.post("/books/", json={
        "title": "Single",
        "author": "Me",
        "description": "Desc",
        "status": "available",
        "year": 2020,
    })
    book_id = create_resp.json()["id"]

    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Single"


def test_get_book_not_found():
    response = client.get("/books/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_delete_book():
    create_resp = client.post("/books/", json={
        "title": "To Delete",
        "author": "Me",
        "description": "Desc",
        "status": "available",
        "year": 2020,
    })
    book_id = create_resp.json()["id"]

    response = client.delete(f"/books/{book_id}")
    assert response.status_code == 204

    get_resp = client.get(f"/books/{book_id}")
    assert get_resp.status_code == 404


def test_filter_by_status():
    client.post("/books/", json={
        "title": "Available", "author": "A",
        "description": "D", "status": "available", "year": 2020,
    })
    client.post("/books/", json={
        "title": "Borrowed", "author": "B",
        "description": "D", "status": "borrowed", "year": 2021,
    })

    response = client.get("/books/?status=available")
    data = response.json()
    assert all(item["status"] == "available" for item in data["items"])