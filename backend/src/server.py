from contextlib import asynccontextmanager
from datetime import datetime
import os
import sys

from bson import ObjectId
from fastapi import fastapi
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
import uvicorn

from dal import ToDoDAL, ListSummary, ToDoList

COLLECTION_NAME = "todo_lists"
MONGODB_URI = os.environ["MONGODB_URI"]
DEBUG = os.environ.get("DEBUG", "").strip().lower() in {"1", "true", "on", "yes"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup 
    client = AsyncIOMotorClient(MONGODB_URI)
    database = client.get_default_database()

    # Ensure the database is available
    pong = await database.command("ping")
    if int(pong["ok"]) != 1:
        raise Exception("Database not available")

    todo_lists = database.get_collection(COLLECTION_NAME)
    app.todo_dal = ToDoDAL(todo_lists)

    # Yield back to FastAPI app
    yield

    # Shutdown
    client.close()

app = FastAPI(lifespan=lifespan, debug=DEBUG)


@app.get("/api/lists")
async def get_all_lists() -> list[ListSummary]:
    return [i async for i in app.todo_dal.list_todo_lists()]


class NewList(BaseModel):
    name: str

class NewListResponse(BaseModel):
    id: str
    name: str

