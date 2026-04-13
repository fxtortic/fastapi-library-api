from fastapi import APIRouter, HTTPException, Depends, Query
from motor.motor_asyncio import AsyncIOMotorCollection
from schemas.book import BookCreate, BookResponse, PaginatedBooks
from services import book_service
from database import book_collection

router = APIRouter(prefix="/books", tags=["Books"])


def get_collection():
    from database import book_collection
    return book_collection

@router.get("/", response_model=PaginatedBooks)
async def get_books(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status: str = None,
    author: str = None,
    sort_by: str = None,
    collection: AsyncIOMotorCollection = Depends(get_collection),
):
    return await book_service.get_books(
        collection, limit, offset, status, author, sort_by
    )


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: str,
    collection: AsyncIOMotorCollection = Depends(get_collection),
):
    book = await book_service.get_book(collection, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", status_code=201, response_model=BookResponse)
async def create_book(
    book: BookCreate,
    collection: AsyncIOMotorCollection = Depends(get_collection),
):
    return await book_service.create_book(collection, book)


@router.delete("/{book_id}", status_code=204)
async def delete_book(
    book_id: str,
    collection: AsyncIOMotorCollection = Depends(get_collection),
):
    deleted = await book_service.delete_book(collection, book_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Book not found")
