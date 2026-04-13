from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from enum import Enum


class BookStatus(str, Enum):
    available = "available"
    borrowed = "borrowed"


class BookCreate(BaseModel):
    title: str = Field(min_length=1)
    author: str
    description: str
    status: BookStatus
    year: int


class BookResponse(BookCreate):
    id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class CursorPaginatedBooks(BaseModel):
    items: list[BookResponse]
    next_cursor: str | None
    has_next: bool
    size: int
