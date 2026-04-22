import os
import redis
from flask import request
from functools import wraps
from services.auth_service import decode_token

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

redis_client = redis.from_url(REDIS_URL)

AUTHENTICATED_LIMIT = 10
ANONYMOUS_LIMIT = 2
WINDOW_SECONDS = 60


def get_rate_limit_info():
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
        payload = decode_token(token)
        if payload and payload.get("type") == "access":
            user_id = payload["sub"]
            return f"rate_limit:user:{user_id}", AUTHENTICATED_LIMIT

    client_ip = request.remote_addr
    return f"rate_limit:ip:{client_ip}", ANONYMOUS_LIMIT


def check_rate_limit(key, limit):
    current = redis_client.get(key)
    if current is None:
        redis_client.setex(key, WINDOW_SECONDS, 1)
        return True, 1, limit
    current = int(current)
    if current >= limit:
        return False, current, limit
    redis_client.incr(key)
    return True, current + 1, limit


def rate_limit(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key, limit = get_rate_limit_info()
        allowed, current, max_limit = check_rate_limit(key, limit)

        if not allowed:
            return {
                "message": "Rate limit exceeded",
                "limit": max_limit,
                "window": f"{WINDOW_SECONDS}s",
            }, 429

        return f(*args, **kwargs)
    return decorated