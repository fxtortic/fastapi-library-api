from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import engine, Base
from api.books import router as books_router

# import models so Base.metadata knows about them
import models.book_data  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="Library API", lifespan=lifespan)
app.include_router(books_router)
