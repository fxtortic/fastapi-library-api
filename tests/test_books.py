import pytest
from main import app
from database import get_db


@pytest.fixture(autouse=True)
def clean_db():
    yield
    db = get_db()
    db.books.drop()
    db.users.drop()


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def get_token(client):
    client.post("/auth/register", json={
        "username": "testuser",
        "password": "testpass123",
    })
    resp = client.post("/auth/login", json={
        "username": "testuser",
        "password": "testpass123",
    })
    return resp.get_json()["access_token"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_register(client):
    resp = client.post("/auth/register", json={
        "username": "newuser",
        "password": "pass123",
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_login(client):
    client.post("/auth/register", json={
        "username": "user1",
        "password": "pass123",
    })
    resp = client.post("/auth/login", json={
        "username": "user1",
        "password": "pass123",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.get_json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "username": "user2",
        "password": "pass123",
    })
    resp = client.post("/auth/login", json={
        "username": "user2",
        "password": "wrong",
    })
    assert resp.status_code == 401


def test_refresh_token(client):
    resp = client.post("/auth/register", json={
        "username": "user3",
        "password": "pass123",
    })
    refresh_token = resp.get_json()["refresh_token"]

    resp2 = client.post("/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert resp2.status_code == 200
    data = resp2.get_json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_books_unauthorized(client):
    resp = client.get("/books/")
    assert resp.status_code == 401


def test_create_book(client):
    token = get_token(client)
    response = client.post("/books/", json={
        "title": "Test Book",
        "author": "Author",
        "description": "Description",
        "status": "available",
        "year": 2024,
    }, headers=auth_header(token))
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "Test Book"
    assert "id" in data


def test_get_books_pagination(client):
    token = get_token(client)
    for i in range(5):
        client.post("/books/", json={
            "title": f"Book {i}",
            "author": "Author",
            "description": "Desc",
            "status": "available",
            "year": 2020 + i,
        }, headers=auth_header(token))

    response = client.get("/books/?limit=2&offset=0", headers=auth_header(token))
    assert response.status_code == 200
    data = response.get_json()
    assert data["total"] == 5
    assert len(data["items"]) == 2

    response2 = client.get("/books/?limit=2&offset=2", headers=auth_header(token))
    data2 = response2.get_json()
    assert len(data2["items"]) == 2


def test_get_book_by_id(client):
    token = get_token(client)
    create_resp = client.post("/books/", json={
        "title": "Single",
        "author": "Me",
        "description": "Desc",
        "status": "available",
        "year": 2020,
    }, headers=auth_header(token))
    book_id = create_resp.get_json()["id"]

    response = client.get(f"/books/{book_id}", headers=auth_header(token))
    assert response.status_code == 200
    assert response.get_json()["title"] == "Single"


def test_delete_book(client):
    token = get_token(client)
    create_resp = client.post("/books/", json={
        "title": "To Delete",
        "author": "Me",
        "description": "Desc",
        "status": "available",
        "year": 2020,
    }, headers=auth_header(token))
    book_id = create_resp.get_json()["id"]

    response = client.delete(f"/books/{book_id}", headers=auth_header(token))
    assert response.status_code == 204

    get_resp = client.get(f"/books/{book_id}", headers=auth_header(token))
    assert get_resp.status_code == 404