from motor.motor_asyncio import AsyncIOMotorCollection
from app.db.database import get_collection
from bson import ObjectId
from typing import Type, TypeVar, Generic, List, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

class BaseRepository(Generic[T]):
    def __init__(self, collection_name: str, model: Type[T]):
        self.collection_name = collection_name
        self.model = model

    async def _get_collection(self) -> AsyncIOMotorCollection:
        logger.info(f"Getting collection: {self.collection_name}")
        try:
            collection = await get_collection(self.collection_name)
            logger.info(f"Successfully obtained collection: {self.collection_name}")
            return collection
        except Exception as e:
            logger.error(f"Failed to get collection {self.collection_name}: {str(e)}")
            logger.error(f"Collection error type: {type(e).__name__}")
            raise

    async def get(self, id: str) -> Optional[T]:
        logger.info(f"Getting document with id: {id} from collection: {self.collection_name}")
        try:
            collection = await self._get_collection()
            logger.info(f"Performing find_one operation for id: {id}")
            document = await collection.find_one({"_id": ObjectId(id)})
            if document:
                logger.info(f"Document found for id: {id}")
                return self.model(**document)
            else:
                logger.warning(f"No document found for id: {id}")
            return None
        except Exception as e:
            logger.error(f"Failed to get document {id} from {self.collection_name}: {str(e)}")
            logger.error(f"Get error type: {type(e).__name__}")
            raise

    async def get_all(self) -> List[T]:
        collection = await self._get_collection()
        return [self.model(**doc) async for doc in collection.find()]

    async def create(self, data: T) -> T:
        collection = await self._get_collection()
        await collection.insert_one(data.model_dump(by_alias=True))
        return data

    async def update(self, id: str, data: BaseModel) -> Optional[T]:
        logger.info(f"Updating document with id: {id} in collection: {self.collection_name}")
        try:
            collection = await self._get_collection()
            logger.info(f"Performing update operation for id: {id}")
            result = await collection.update_one(
                {"_id": ObjectId(id)}, {"$set": data.model_dump(exclude_unset=True)}
            )
            logger.info(f"Update operation completed. Modified count: {result.modified_count}")
            return await self.get(id)
        except Exception as e:
            logger.error(f"Failed to update document {id} in {self.collection_name}: {str(e)}")
            logger.error(f"Update error type: {type(e).__name__}")
            raise

    async def delete(self, id: str) -> bool:
        collection = await self._get_collection()
        result = await collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0