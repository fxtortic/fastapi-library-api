from uuid import UUID, uuid4
from motor.motor_asyncio import AsyncIOMotorDatabase
from repository import book_repository
from schemas.book import BookCreate, PaginatedBooks, BookResponse


async def get_books(
    db: AsyncIOMotorDatabase,
    limit: int,
    offset: int,
    status: str | None = None,
    author: str | None = None,
) -> PaginatedBooks:
    books, total = await book_repository.get_all_books(
        db, limit, offset, status, author
    )
    return PaginatedBooks(
        items=[BookResponse(**_fix_id(b)) for b in books],
        total=total,
        limit=limit,
        offset=offset,
    )


async def get_book(db: AsyncIOMotorDatabase, book_id: UUID) -> BookResponse | None:
    book = await book_repository.get_book_by_id(db, book_id)
    if not book:
        return None
    return BookResponse(**_fix_id(book))


async def create_book(db: AsyncIOMotorDatabase, book_data: BookCreate) -> BookResponse:
    data = book_data.model_dump()
    data["id"] = uuid4()
    created = await book_repository.add_book(db, data)
    return BookResponse(**created)


async def delete_book(db: AsyncIOMotorDatabase, book_id: UUID) -> bool:
    return await book_repository.delete_book(db, book_id)


def _fix_id(doc: dict) -> dict:
    """MongoDB uses _id, our schema expects id."""
    if "_id" in doc and "id" not in doc:
        doc["id"] = doc.pop("_id")
    return doc