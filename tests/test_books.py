import pytest
from main import app
from database import get_db


@pytest.fixture(autouse=True)
def clean_db():
    yield
    db = get_db()
    db.books.drop()


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_create_book(client):
    response = client.post("/books/", json={
        "title": "Test Book",
        "author": "Author",
        "description": "Description",
        "status": "available",
        "year": 2024,
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Test Book"
    assert "id" in data


def test_get_books_pagination(client):
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
    data = response.get_json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["limit"] == 2
    assert data["offset"] == 0

    response2 = client.get("/books/?limit=2&offset=2")
    data2 = response2.get_json()
    assert len(data2["items"]) == 2
    assert data2["offset"] == 2


def test_get_book_by_id(client):
    create_resp = client.post("/books/", json={
        "title": "Single",
        "author": "Me",
        "description": "Desc",
        "status": "available",
        "year": 2020,
    })
    book_id = create_resp.get_json()["id"]

    response = client.get(f"/books/{book_id}")
    assert response.status_code == 200
    assert response.get_json()["title"] == "Single"


def test_get_book_not_found(client):
    response = client.get("/books/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_delete_book(client):
    create_resp = client.post("/books/", json={
        "title": "To Delete",
        "author": "Me",
        "description": "Desc",
        "status": "available",
        "year": 2020,
    })
    book_id = create_resp.get_json()["id"]

    response = client.delete(f"/books/{book_id}")
    assert response.status_code == 204

    get_resp = client.get(f"/books/{book_id}")
    assert get_resp.status_code == 404


def test_filter_by_status(client):
    client.post("/books/", json={
        "title": "Available",
        "author": "A",
        "description": "D",
        "status": "available",
        "year": 2020,
    })
    client.post("/books/", json={
        "title": "Borrowed",
        "author": "B",
        "description": "D",
        "status": "borrowed",
        "year": 2021,
    })

    response = client.get("/books/?status=available")
    data = response.get_json()
    assert all(item["status"] == "available" for item in data["items"])