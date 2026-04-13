from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.book_data import Book


async def get_all_books(
    db: AsyncSession,
    limit: int,
    offset: int,
    status: str | None = None,
    author: str | None = None,
    sort_by: str | None = None,
) -> tuple[list[Book], int]:
    query = select(Book)
    count_query = select(func.count()).select_from(Book)

    if status:
        query = query.where(Book.status == status)
        count_query = count_query.where(Book.status == status)

    if author:
        query = query.where(Book.author == author)
        count_query = count_query.where(Book.author == author)

    if sort_by == "title":
        query = query.order_by(Book.title)
    elif sort_by == "year":
        query = query.order_by(Book.year)
    else:
        query = query.order_by(Book.title)

    total = await db.scalar(count_query)
    result = await db.execute(query.limit(limit).offset(offset))
    books = list(result.scalars().all())

    return books, total


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
