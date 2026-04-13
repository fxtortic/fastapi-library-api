from motor.motor_asyncio import AsyncIOMotorCollection
from repository import book_repository
from schemas.book import BookCreate, BookResponse, PaginatedBooks


async def get_books(
    collection: AsyncIOMotorCollection,
    limit: int,
    offset: int,
    status: str | None = None,
    author: str | None = None,
    sort_by: str | None = None,
) -> PaginatedBooks:
    books, total = await book_repository.get_all_books(
        collection, limit, offset, status, author, sort_by
    )
    return PaginatedBooks(
        items=[BookResponse.model_validate(b) for b in books],
        total=total,
        limit=limit,
        offset=offset,
    )


async def get_book(
    collection: AsyncIOMotorCollection,
    book_id: str,
) -> BookResponse | None:
    book = await book_repository.get_book_by_id(collection, book_id)
    if not book:
        return None
    return BookResponse.model_validate(book)


async def create_book(
    collection: AsyncIOMotorCollection,
    book_data: BookCreate,
) -> BookResponse:
    created = await book_repository.add_book(collection, book_data)
    return BookResponse.model_validate(created)


async def delete_book(
    collection: AsyncIOMotorCollection,
    book_id: str,
) -> bool:
    return await book_repository.delete_book(collection, book_id)
