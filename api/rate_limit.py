from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from schemas.book import BookCreateSchema, BookResponseSchema, PaginatedBooksSchema
from services import book_service
from api.auth_decorator import token_required
from rate_limiter import rate_limit

book_create_schema = BookCreateSchema()
book_response_schema = BookResponseSchema()
paginated_schema = PaginatedBooksSchema()


class BookListResource(Resource):
    method_decorators = [token_required, rate_limit]

    def get(self):
        """Get books with pagination
        ---
        tags:
          - Books
        security:
          - Bearer: []
        parameters:
          - name: limit
            in: query
            type: integer
            default: 10
          - name: offset
            in: query
            type: integer
            default: 0
          - name: status
            in: query
            type: string
            enum: [available, borrowed]
            required: false
          - name: author
            in: query
            type: string
            required: false
        responses:
          200:
            description: Paginated list of books
            schema:
              $ref: '#/definitions/PaginatedBooks'
          401:
            description: Unauthorized
          429:
            description: Rate limit exceeded
        """
        limit = request.args.get("limit", 10, type=int)
        offset = request.args.get("offset", 0, type=int)
        status = request.args.get("status")
        author = request.args.get("author")

        limit = max(1, min(limit, 100))
        offset = max(0, offset)

        result = book_service.get_books(limit, offset, status, author)
        return paginated_schema.dump(result), 200

    def post(self):
        """Create a new book
        ---
        tags:
          - Books
        security:
          - Bearer: []
        parameters:
          - in: body
            name: body
            required: true
            schema:
              $ref: '#/definitions/BookCreate'
        responses:
          201:
            description: Book created
            schema:
              $ref: '#/definitions/BookResponse'
          400:
            description: Validation error
          401:
            description: Unauthorized
          429:
            description: Rate limit exceeded
        """
        json_data = request.get_json()
        if not json_data:
            return {"message": "No input data"}, 400

        try:
            data = book_create_schema.load(json_data)
        except ValidationError as err:
            return {"errors": err.messages}, 400

        book = book_service.create_book(data)
        return book_response_schema.dump(book), 201


class BookResource(Resource):
    method_decorators = [token_required, rate_limit]

    def get(self, book_id):
        """Get a book by ID
        ---
        tags:
          - Books
        security:
          - Bearer: []
        parameters:
          - name: book_id
            in: path
            type: string
            required: true
        responses:
          200:
            description: Book found
            schema:
              $ref: '#/definitions/BookResponse'
          401:
            description: Unauthorized
          404:
            description: Book not found
          429:
            description: Rate limit exceeded
        """
        book = book_service.get_book(book_id)
        if not book:
            return {"message": "Book not found"}, 404
        return book_response_schema.dump(book), 200

    def delete(self, book_id):
        """Delete a book
        ---
        tags:
          - Books
        security:
          - Bearer: []
        parameters:
          - name: book_id
            in: path
            type: string
            required: true
        responses:
          204:
            description: Book deleted
          401:
            description: Unauthorized
          404:
            description: Book not found
          429:
            description: Rate limit exceeded
        """
        deleted = book_service.delete_book(book_id)
        if not deleted:
            return {"message": "Book not found"}, 404
        return "", 204