from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.chat import chat
from app.core.postgres import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
     create_db_and_tables()
     yield


app = FastAPI(
    title="HP RAG API",
    version="0.0.1",
)

app.include_router(chat.router, prefix="/api/v1")

@app.get("/healthcheck")
def healthcheck():
    return {
        "data": "OK",
        "message": "Health check passed",
        "statusCode": 200,
        "success": True
    }