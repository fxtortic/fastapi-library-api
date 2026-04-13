from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import init_db
from api.books import router as books_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Library API (MongoDB)", lifespan=lifespan)
app.include_router(books_router)