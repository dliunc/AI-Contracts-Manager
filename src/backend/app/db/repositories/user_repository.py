from app.db.repository import BaseRepository
from app.models.user import User
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(collection_name="users", model=User)

    async def get_by_username(self, db, *, username: str) -> Optional[User]:
        collection = await self._get_collection()
        user_data = await collection.find_one({"username": username})
        if user_data:
            return User(**user_data)
        return None
    async def get_by_id(self, user_id: str) -> Optional[User]:
        logger.info(f"Getting user by id: {user_id}")
        try:
            collection = await self._get_collection()
            logger.info(f"Performing find_one operation for user id: {user_id}")
            user_data = await collection.find_one({"id": user_id})
            if user_data:
                logger.info(f"User found for id: {user_id}")
                return User(**user_data)
            else:
                logger.warning(f"No user found for id: {user_id}")
            return None
        except Exception as e:
            logger.error(f"Failed to get user by id {user_id}: {str(e)}")
            logger.error(f"User get_by_id error type: {type(e).__name__}")
            raise