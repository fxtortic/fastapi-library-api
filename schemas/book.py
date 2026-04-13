from pydantic import BaseModel, Field
from uuid import UUID
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

    model_config = {"from_attributes": True}


class PaginatedBooks(BaseModel):
    items: list[BookResponse]
    total: int
    limit: int
    offset: int
