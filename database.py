import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "library_db")

client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DB]


def get_db():
    return db