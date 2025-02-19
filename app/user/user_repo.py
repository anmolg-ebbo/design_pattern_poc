# app/user/user_repo.py
from typing import Optional, List
from app.user.user_model import User, UserStatus
from app.common.base_repo import BaseRepository
from core.db.database import MongoDBConnection

class UserRepository(BaseRepository[User]):
    def __init__(self, db: MongoDBConnection):
        super().__init__(User, "users", db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        doc = await self.collection.find_one({"email": email, "is_deleted": False})
        return User.model_validate(doc) if doc else None

    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        doc = await self.collection.find_one({"username": username, "is_deleted": False})
        return User.model_validate(doc) if doc else None

    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get active users with pagination"""
        cursor = self.collection.find({
            "is_deleted": False,
            "status": UserStatus.ACTIVE
        }).skip(skip).limit(limit)
        return [User.model_validate(doc) async for doc in cursor]