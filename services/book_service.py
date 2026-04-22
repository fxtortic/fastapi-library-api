from uuid import uuid4
from repository import book_repository
from database import get_db


def _fix_id(doc: dict) -> dict:
    if "_id" in doc and "id" not in doc:
        doc["id"] = doc.pop("_id")
    return doc


def get_books(limit: int, offset: int, status: str = None, author: str = None) -> dict:
    db = get_db()
    books, total = book_repository.get_all_books(db, limit, offset, status, author)
    return {
        "items": [_fix_id(b) for b in books],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


def get_book(book_id: str) -> dict | None:
    db = get_db()
    book = book_repository.get_book_by_id(db, book_id)
    if not book:
        return None
    return _fix_id(book)


def create_book(book_data: dict) -> dict:
    db = get_db()
    book_data["id"] = str(uuid4())
    created = book_repository.add_book(db, book_data)
    return created


def delete_book(book_id: str) -> bool:
    db = get_db()
    return book_repository.delete_book(db, book_id)