import os
import motor.motor_asyncio

MONGO_URL = os.getenv(
    "MONGO_URL",
    "mongodb://mongo_admin:password@localhost:27017/?authSource=admin"
)
MONGO_DB = os.getenv("MONGO_DB", "books")

client = None
database = None
book_collection = None


def init_db():
    global client, database, book_collection
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
    database = client[MONGO_DB]
    book_collection = database["books"]