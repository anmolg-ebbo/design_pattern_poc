from abc import ABC, abstractmethod
from typing import Optional
from app.user.user_model import User


class IUserService(ABC):
    @abstractmethod
    async def create_user(self, user_data: dict) -> User:
        """Creates a new user"""
        pass

    @abstractmethod
    async def get_user(self, user_id: str) -> Optional[User]:
        """Fetch a user by ID"""
        pass

    @abstractmethod
    async def update_user(self, user_id: str, user_data: dict) -> User:
        """Update user details"""
        pass

    @abstractmethod
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user by ID"""
        pass