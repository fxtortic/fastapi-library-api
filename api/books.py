from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.book import BookCreate, BookResponse, CursorPaginatedBooks
from services import book_service
from database import get_db
from uuid import UUID

router = APIRouter(prefix="/books", tags=["Books"])


@router.get("/", response_model=CursorPaginatedBooks)
async def get_books(
    size: int = Query(default=10, ge=1, le=100),
    cursor: str | None = Query(default=None),
    status: str = None,
    author: str = None,
    db: AsyncSession = Depends(get_db),
):
    return await book_service.get_books(db, size, cursor, status, author)


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(book_id: UUID, db: AsyncSession = Depends(get_db)):
    book = await book_service.get_book(db, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("/", status_code=201, response_model=BookResponse)
async def create_book(book: BookCreate, db: AsyncSession = Depends(get_db)):
    return await book_service.create_book(db, book)


@router.delete("/{book_id}", status_code=204)
async def delete_book(book_id: UUID, db: AsyncSession = Depends(get_db)):
    deleted = await book_service.delete_book(db, book_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Book not found")
