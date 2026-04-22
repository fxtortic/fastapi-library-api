from flask import Flask
from flask_restful import Api
from flasgger import Swagger
from api.books import BookListResource, BookResource

app = Flask(__name__)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/",
}

swagger_template = {
    "info": {
        "title": "Library API",
        "version": "1.0",
    },
    "definitions": {
        "BookCreate": {
            "type": "object",
            "required": ["title", "author", "description", "status", "year"],
            "properties": {
                "title": {"type": "string", "minLength": 1},
                "author": {"type": "string"},
                "description": {"type": "string"},
                "status": {"type": "string", "enum": ["available", "borrowed"]},
                "year": {"type": "integer"},
            },
        },
        "BookResponse": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "title": {"type": "string"},
                "author": {"type": "string"},
                "description": {"type": "string"},
                "status": {"type": "string"},
                "year": {"type": "integer"},
            },
        },
        "PaginatedBooks": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/BookResponse"},
                },
                "total": {"type": "integer"},
                "limit": {"type": "integer"},
                "offset": {"type": "integer"},
            },
        },
    },
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)
api = Api(app)

api.add_resource(BookListResource, "/books/")
api.add_resource(BookResource, "/books/<string:book_id>")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)