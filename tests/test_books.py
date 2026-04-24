import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from database import Base, get_db
from main import app

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5433/library_test_db?ssl=disable"
)

test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestSession = async_sessionmaker(test_engine, expire_on_commit=False)


async def override_get_db():
    async with TestSession() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_book(client: AsyncClient):
    response = await client.post("/books/", json={
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
    assert "created_at" in data


@pytest.mark.asyncio
async def test_get_books_cursor_pagination(client: AsyncClient):
    for i in range(5):
        await client.post("/books/", json={
            "title": f"Book {i}",
            "author": "Author",
            "description": "Desc",
            "status": "available",
            "year": 2020 + i,
        })

    # first page
    response = await client.get("/books/?size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["has_next"] is True
    assert data["next_cursor"] is not None
    assert data["size"] == 2

    # second page using cursor
    cursor = data["next_cursor"]
    response2 = await client.get(f"/books/?size=2&cursor={cursor}")
    data2 = response2.json()
    assert len(data2["items"]) == 2
    assert data2["has_next"] is True

    # verify no overlap between pages
    ids_page1 = {item["id"] for item in data["items"]}
    ids_page2 = {item["id"] for item in data2["items"]}
    assert ids_page1.isdisjoint(ids_page2)

    # third page — last item
    cursor2 = data2["next_cursor"]
    response3 = await client.get(f"/books/?size=2&cursor={cursor2}")
    data3 = response3.json()
    assert len(data3["items"]) == 1
    assert data3["has_next"] is False
    assert data3["next_cursor"] is None


@pytest.mark.asyncio
async def test_get_book_by_id(client: AsyncClient):
    create_resp = await client.post("/books/", json={
        "title": "Single",
        "author": "Me",
        "description": "Desc",
        "status": "available",
        "year": 2020,
    })
    book_id = create_resp.json()["id"]

    response = await client.get(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Single"


@pytest.mark.asyncio
async def test_get_book_not_found(client: AsyncClient):
    response = await client.get("/books/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_book(client: AsyncClient):
    create_resp = await client.post("/books/", json={
        "title": "To Delete",
        "author": "Me",
        "description": "Desc",
        "status": "available",
        "year": 2020,
    })
    book_id = create_resp.json()["id"]

    response = await client.delete(f"/books/{book_id}")
    assert response.status_code == 204

    get_resp = await client.get(f"/books/{book_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_filter_by_status(client: AsyncClient):
    await client.post("/books/", json={
        "title": "Available",
        "author": "A",
        "description": "D",
        "status": "available",
        "year": 2020,
    })
    await client.post("/books/", json={
        "title": "Borrowed",
        "author": "B",
        "description": "D",
        "status": "borrowed",
        "year": 2021,
    })

    response = await client.get("/books/?status=available")
    data = response.json()
    assert all(item["status"] == "available" for item in data["items"])