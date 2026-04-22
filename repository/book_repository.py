from uuid import UUID, uuid4
from motor.motor_asyncio import AsyncIOMotorDatabase


async def get_all_books(
    db: AsyncIOMotorDatabase,
    limit: int,
    offset: int,
    status: str | None = None,
    author: str | None = None,
) -> tuple[list[dict], int]:
    filter_query = {}
    if status:
        filter_query["status"] = status
    if author:
        filter_query["author"] = author

    total = await db.books.count_documents(filter_query)
    cursor = db.books.find(filter_query).skip(offset).limit(limit)
    books = await cursor.to_list(length=limit)

    return books, total


async def get_book_by_id(db: AsyncIOMotorDatabase, book_id: UUID) -> dict | None:
    return await db.books.find_one({"_id": str(book_id)})


async def add_book(db: AsyncIOMotorDatabase, book_data: dict) -> dict:
    book_data["_id"] = str(book_data.pop("id", uuid4()))
    await db.books.insert_one(book_data)
    book_data["id"] = book_data.pop("_id")
    return book_data


async def delete_book(db: AsyncIOMotorDatabase, book_id: UUID) -> bool:
    result = await db.books.delete_one({"_id": str(book_id)})
    return result.deleted_count > 0