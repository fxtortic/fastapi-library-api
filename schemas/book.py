from pydantic import BaseModel, Field
from enum import Enum
from typing import Annotated
from bson import ObjectId


class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, _info=None):
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_core_schema__(cls, _source, _handler):
        from pydantic import GetCoreSchemaHandler
        from pydantic_core import core_schema

        return core_schema.no_info_plain_validator_function(
            cls.validate,
            serialization=core_schema.to_string_ser_schema(),
        )


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
    id: PyObjectId = Field(alias="_id")

    model_config = {"populate_by_name": True}


class PaginatedBooks(BaseModel):
    items: list[BookResponse]
    total: int
    limit: int
    offset: int
