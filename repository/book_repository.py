from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from models.book_data import book_to_document
from schemas.book import BookCreate


async def get_all_books(
    collection: AsyncIOMotorCollection,
    limit: int,
    offset: int,
    status: str | None = None,
    author: str | None = None,
    sort_by: str | None = None,
) -> tuple[list[dict], int]:
    query = {}

    if status:
        query["status"] = status
    if author:
        query["author"] = author

    total = await collection.count_documents(query)

    cursor = collection.find(query).skip(offset).limit(limit)

    if sort_by in ("title", "year"):
        cursor = cursor.sort(sort_by, 1)

    books = await cursor.to_list(length=limit)
    return books, total


async def get_book_by_id(
    collection: AsyncIOMotorCollection,
    book_id: str,
) -> dict | None:
    return await collection.find_one({"_id": ObjectId(book_id)})


async def add_book(
    collection: AsyncIOMotorCollection,
    book_data: BookCreate,
) -> dict:
    document = book_to_document(book_data)
    result = await collection.insert_one(document)
    return await collection.find_one({"_id": result.inserted_id})


async def delete_book(
    collection: AsyncIOMotorCollection,
    book_id: str,
) -> bool:
    response = await collection.delete_one({"_id": ObjectId(book_id)})
    return response.deleted_count > 0
