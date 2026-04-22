import os
import jwt
import bcrypt
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from database import get_db
from repository import user_repository

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-key-change-me")
ACCESS_TOKEN_EXPIRE = 15  # minutes
REFRESH_TOKEN_EXPIRE = 7  # days


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_access_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "type": "refresh",
        "jti": str(uuid4()),
        "exp": datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def register(username: str, password: str) -> dict | None:
    db = get_db()
    if user_repository.find_by_username(db, username):
        return None

    user = {
        "_id": str(uuid4()),
        "username": username,
        "password": hash_password(password),
    }
    user_repository.create_user(db, user)

    return {
        "access_token": create_access_token(user["_id"]),
        "refresh_token": create_refresh_token(user["_id"]),
    }


def login(username: str, password: str) -> dict | None:
    db = get_db()
    user = user_repository.find_by_username(db, username)
    if not user or not verify_password(password, user["password"]):
        return None

    return {
        "access_token": create_access_token(user["_id"]),
        "refresh_token": create_refresh_token(user["_id"]),
    }


def refresh(refresh_token: str) -> dict | None:
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        return None

    user_id = payload["sub"]
    return {
        "access_token": create_access_token(user_id),
        "refresh_token": create_refresh_token(user_id),
    }