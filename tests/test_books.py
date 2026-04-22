import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient

from database import get_db
from main import app

MONGO_TEST_URL = "mongodb://localhost:27017"
MONGO_TEST_DB = "library_test_db"

test_client = AsyncIOMotorClient(MONGO_TEST_URL)
test_db = test_client[MONGO_TEST_DB]


def override_get_db():
    return test_db


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    yield
    await test_db.books.drop()


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


@pytest.mark.asyncio
async def test_get_books_pagination(client: AsyncClient):
    for i in range(5):
        await client.post("/books/", json={
            "title": f"Book {i}",
            "author": "Author",
            "description": "Desc",
            "status": "available",
            "year": 2020 + i,
        })

    response = await client.get("/books/?limit=2&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["limit"] == 2
    assert data["offset"] == 0

    response2 = await client.get("/books/?limit=2&offset=2")
    data2 = response2.json()
    assert len(data2["items"]) == 2
    assert data2["offset"] == 2


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