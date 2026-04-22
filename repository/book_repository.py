from uuid import UUID, uuid4
from pymongo.database import Database


def get_all_books(db: Database, limit: int, offset: int,
                  status: str = None, author: str = None) -> tuple:
    filter_query = {}
    if status:
        filter_query["status"] = status
    if author:
        filter_query["author"] = author

    total = db.books.count_documents(filter_query)
    books = list(db.books.find(filter_query).skip(offset).limit(limit))

    return books, total


def get_book_by_id(db: Database, book_id: str) -> dict | None:
    return db.books.find_one({"_id": book_id})


def add_book(db: Database, book_data: dict) -> dict:
    book_data["_id"] = str(book_data.pop("id", uuid4()))
    db.books.insert_one(book_data)
    book_data["id"] = book_data.pop("_id")
    return book_data


def delete_book(db: Database, book_id: str) -> bool:
    result = db.books.delete_one({"_id": book_id})
    return result.deleted_count > 0