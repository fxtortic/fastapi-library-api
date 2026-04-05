from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_book():
    response = client.post("/books/", json={
        "title": "Test",
        "author": "Me",
        "description": "Desc",
        "status": "available",
        "year": 2020
    })
    assert response.status_code == 201
    assert "id" in response.json()

def test_get_books():
    response = client.get("/books/")
    assert response.status_code == 200

def test_delete_book():
    create = client.post("/books/", json={
        "title": "Delete",
        "author": "Me",
        "description": "Desc",
        "status": "available",
        "year": 2020
    })

    book_id = create.json()["id"]

    response = client.delete(f"/books/{book_id}")
    assert response.status_code == 204