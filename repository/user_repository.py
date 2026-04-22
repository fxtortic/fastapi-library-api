from pymongo.database import Database


def find_by_username(db: Database, username: str) -> dict | None:
    return db.users.find_one({"username": username})


def create_user(db: Database, user_data: dict) -> dict:
    db.users.insert_one(user_data)
    return user_data