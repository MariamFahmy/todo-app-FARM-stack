# dal stands for data access layer
"""Handles all interactions between the application and the database"""

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReturnDocument
from pydantic import BaseModel
from uuid import uuid4

class ListSummary(BaseModel):
    id: str
    name: str
    item_count: int

    @staticmethod
    # create instances from MongoDB documents
    def from_doc(doc) -> "ListSummary":
        return ListSummary(
            id=str(doc["_id"]),
            name=doc["name"],
            item_count=doc["item_count"],
        )

class ToDoListItem(BaseModel):
    id: str
    label: str
    checked: bool

    @staticmethod
    def from_doc(item) -> "ToDoListItem":
        return ToDoListItem(
            id=item["id"],
            label=item["label"],
            checked=item["checked"],
        )

class ToDoList(BaseModel):
    id: str
    name: str
    items: list[ToDoListItem]

    @staticmethod
    def from_doc(doc) -> "ToDoList":
        return ToDoList(
            id=str(doc["_id"])
            name=doc["name"],
            items=[ToDoListItem.from_doc(item) for item in doc["items"]],
        )

class ToDoDAL:
    """Encapsulate all database operations"""

    def __init__(self, todo_collection: AsyncIOMotorCollection) {
        self._todo_collection = todo_collection
    }

    async def list_todo_lists(self, session=None):
        """Asynchronously yields summaries of all to-do lists from MongoDB database"""
        async for doc in self._todo_collection.find(
            {},
            projection={
                "name": 1,
                "item_count": {"$size": "$items"},
            },
            sort={"name": 1},
            session=session,
        ):
            yield ListSummary.from_doc(doc)

    async def create_todo_list(self, name:str, session=None) -> str:
        response = await self._todo_collection.insert_one(
            {"name": name, "items": []},
            session=session,
        )
        return str(response.inserted_id)

    async def get_todo_list(self, id: str | ObjectId, session=None) -> ToDoList:
        

    