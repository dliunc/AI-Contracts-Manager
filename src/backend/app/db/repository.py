from motor.motor_asyncio import AsyncIOMotorCollection
from app.db.database import get_collection
from bson import ObjectId
from typing import Type, TypeVar, Generic, List, Optional
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class BaseRepository(Generic[T]):
    def __init__(self, collection_name: str, model: Type[T]):
        self.collection_name = collection_name
        self.model = model

    async def _get_collection(self) -> AsyncIOMotorCollection:
        return await get_collection(self.collection_name)

    async def get(self, id: str) -> Optional[T]:
        collection = await self._get_collection()
        document = await collection.find_one({"_id": ObjectId(id)})
        if document:
            return self.model(**document)
        return None

    async def get_all(self) -> List[T]:
        collection = await self._get_collection()
        return [self.model(**doc) async for doc in collection.find()]

    async def create(self, data: T) -> T:
        collection = await self._get_collection()
        await collection.insert_one(data.model_dump(by_alias=True))
        return data

    async def update(self, id: str, data: BaseModel) -> Optional[T]:
        collection = await self._get_collection()
        await collection.update_one(
            {"_id": ObjectId(id)}, {"$set": data.model_dump(exclude_unset=True)}
        )
        return await self.get(id)

    async def delete(self, id: str) -> bool:
        collection = await self._get_collection()
        result = await collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0