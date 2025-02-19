# app/user/interfaces/i_user_repo.py
from abc import ABC, abstractmethod
from typing import Optional, List
from app.common.base_repo import BaseRepository
from app.user.user_model import User, UserStatus

class IUserRepository(BaseRepository[User], ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    async def update_last_login(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    async def update_status(self, user_id: str, status: UserStatus) -> Optional[User]:
        pass

    @abstractmethod
    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        pass

    @abstractmethod
    async def get_users_by_role(self, role: str, skip: int = 0, limit: int = 100) -> List[User]:
        pass