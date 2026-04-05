from models.book_data import books_db

async def get_all_books():
    return books_db

async def get_book_by_id(book_id):
    for book in books_db:
        if book["id"] == book_id:
            return book
    return None

async def add_book(book):
    books_db.append(book)
    return book

async def delete_book(book_id):
    global books_db
    initial_len = len(books_db)
    books_db = [b for b in books_db if b["id"] != book_id]
    return len(books_db) != initial_len