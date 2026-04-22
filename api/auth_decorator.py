from functools import wraps
from flask import request
from services.auth_service import decode_token


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return {"message": "Missing or invalid token"}, 401

        token = auth_header.split(" ", 1)[1]
        payload = decode_token(token)

        if not payload or payload.get("type") != "access":
            return {"message": "Invalid or expired access token"}, 401

        return f(*args, **kwargs)
    return decorated