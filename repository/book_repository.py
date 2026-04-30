import base64
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from models.book_data import Book


def encode_cursor(created_at: datetime, book_id: UUID) -> str:
    raw = f"{created_at.isoformat()}|{book_id}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def decode_cursor(cursor: str) -> tuple[datetime, UUID]:
    raw = base64.urlsafe_b64decode(cursor.encode()).decode()
    ts_str, id_str = raw.split("|", 1)
    return datetime.fromisoformat(ts_str), UUID(id_str)


async def get_all_books(
    db: AsyncSession,
    size: int,
    cursor: str | None = None,
    status: str | None = None,
    author: str | None = None,
) -> tuple[list[Book], str | None, bool]:
    query = select(Book)

    if status:
        query = query.where(Book.status == status)
    if author:
        query = query.where(Book.author == author)

    if cursor:
        cursor_ts, cursor_id = decode_cursor(cursor)
        query = query.where(
            or_(
                Book.created_at > cursor_ts,
                and_(Book.created_at == cursor_ts, Book.id > cursor_id),
            )
        )
    query = query.order_by(Book.created_at, Book.id).limit(size + 1)

    result = await db.execute(query)
    books = list(result.scalars().all())

    has_next = len(books) > size
    if has_next:
        books = books[:size]

    next_cursor = None
    if has_next and books:
        last = books[-1]
        next_cursor = encode_cursor(last.created_at, last.id)

    return books, next_cursor, has_next


async def get_book_by_id(db: AsyncSession, book_id: UUID) -> Book | None:
    result = await db.execute(select(Book).where(Book.id == book_id))
    return result.scalar_one_or_none()


async def add_book(db: AsyncSession, book: Book) -> Book:
    db.add(book)
    await db.commit()
    await db.refresh(book)
    return book


async def delete_book(db: AsyncSession, book_id: UUID) -> bool:
    book = await get_book_by_id(db, book_id)
    if not book:
        return False
    await db.delete(book)
    await db.commit()
    return True
