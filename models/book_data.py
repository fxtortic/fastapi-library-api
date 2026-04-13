from schemas.book import BookCreate


def book_to_document(book_data: BookCreate) -> dict:
    """Convert Pydantic schema to MongoDB document."""
    return book_data.model_dump()


def document_to_dict(document: dict) -> dict:
    """Normalize MongoDB document for API response."""
    if document and "_id" in document:
        document["_id"] = str(document["_id"])
    return document
