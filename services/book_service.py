from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from repository import book_repository
from schemas.book import BookCreate, CursorPaginatedBooks, BookResponse
from models.book_data import Book


async def get_books(
    db: AsyncSession,
    size: int,
    cursor: str | None = None,
    status: str | None = None,
    author: str | None = None,
) -> CursorPaginatedBooks:
    books, next_cursor, has_next = await book_repository.get_all_books(
        db, size, cursor, status, author
    )
    return CursorPaginatedBooks(
        items=[BookResponse.model_validate(b) for b in books],
        next_cursor=next_cursor,
        has_next=has_next,
        size=size,
    )


async def get_book(db: AsyncSession, book_id: UUID) -> BookResponse | None:
    book = await book_repository.get_book_by_id(db, book_id)
    if not book:
        return None
    return BookResponse.model_validate(book)


async def create_book(db: AsyncSession, book_data: BookCreate) -> BookResponse:
    book = Book(id=uuid4(), **book_data.model_dump())
    created = await book_repository.add_book(db, book)
    return BookResponse.model_validate(created)


async def delete_book(db: AsyncSession, book_id: UUID) -> bool:
    return await book_repository.delete_book(db, book_id)
