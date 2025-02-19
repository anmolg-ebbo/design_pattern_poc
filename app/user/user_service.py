# app/user/user_service.py
from typing import Optional, List, Dict, Any
from fastapi import HTTPException
import bcrypt
from app.user.interfaces.i_user_service import IUserService
from app.user.user_model import User
from app.user.user_repo import UserRepository

class UserService(IUserService):
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def create_user(self, user_data: dict) -> User:
        """Creates a new user with hashed password."""
        if not isinstance(user_data, dict):
            raise ValueError(f"Invalid user_data format: Expected dict, got {type(user_data)}")

        print(user_data)
        if await self.user_repository.get_by_email(user_data["email"]):
            raise HTTPException(status_code=400, detail="Email already registered")
        if await self.user_repository.get_by_username(user_data["username"]):
            raise HTTPException(status_code=400, detail="Username already taken")

        # Extract and hash password before storing
        password = user_data.pop("password", None)
        if not password:
            raise HTTPException(status_code=400, detail="Password is required")

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user_data["password_hash"] = hashed_password  # Store hashed password

        user = User(**user_data)
        return await self.user_repository.create(user)

    async def get_user(self, user_id: str) -> Optional[User]:
        """Fetch user by ID, raise error if not found."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
        
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        return await self.user_repository.get_all(skip, limit)

    async def update_user(self, user_id: str, user_data: Dict[str, Any]) -> User:
        """Update user details."""
        # Handle password updates separately if needed
        if "password" in user_data:
            password = user_data.pop("password")
            user_data["password_hash"] = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            
        updated_user = await self.user_repository.update(user_id, user_data)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        return await self.user_repository.delete(user_id)