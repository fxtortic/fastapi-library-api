from marshmallow import Schema, fields, validate


class BookCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1))
    author = fields.Str(required=True)
    description = fields.Str(required=True)
    status = fields.Str(required=True, validate=validate.OneOf(["available", "borrowed"]))
    year = fields.Int(required=True)


class BookResponseSchema(BookCreateSchema):
    id = fields.Str(required=True)


class PaginatedBooksSchema(Schema):
    items = fields.List(fields.Nested(BookResponseSchema))
    total = fields.Int()
    limit = fields.Int()
    offset = fields.Int()