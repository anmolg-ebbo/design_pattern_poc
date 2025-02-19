# app/user/user_repo.py
from typing import Optional, List
from datetime import datetime
from app.user.interfaces.i_user_repo import IUserRepository
from app.user.user_model import User, UserStatus
from core.db.database import MongoDBConnection

class UserRepository(IUserRepository):
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

    async def update_last_login(self, user_id: str) -> Optional[User]:
        """Update user's last login timestamp"""
        return await self.update(user_id, {"last_login": datetime.utcnow()})

    async def update_status(self, user_id: str, status: UserStatus) -> Optional[User]:
        """Update user's status"""
        return await self.update(user_id, {"status": status})

    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get active users with pagination"""
        cursor = self.collection.find({
            "is_deleted": False,
            "status": UserStatus.ACTIVE
        }).skip(skip).limit(limit)
        return [User.model_validate(doc) async for doc in cursor]
    
    async def get_users_by_role(self, role: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by role with pagination"""
        cursor = self.collection.find({
            "is_deleted": False,
            "roles": role
        }).skip(skip).limit(limit)
        return [User.model_validate(doc) async for doc in cursor]