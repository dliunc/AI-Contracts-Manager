from app.db.repository import BaseRepository
from app.models.user import User
from typing import Optional

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
        collection = await self._get_collection()
        user_data = await collection.find_one({"id": user_id})
        if user_data:
            return User(**user_data)
        return None