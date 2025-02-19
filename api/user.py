# api/routes/user_routes.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.user.user_service import UserService
from app.user.user_model import User
from app.user.schemas.user_create_request import UserCreateRequest, UserUpdateRequest
from api.dependencies import get_user_service

user_router = APIRouter()

@user_router.post("/users", response_model=User)
async def create_user(user_data: UserCreateRequest, service: UserService = Depends(get_user_service)):
    try:
        print(user_data)
        user = await service.create_user(user_data.model_dump())
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@user_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str, service: UserService = Depends(get_user_service)):
    try:
        user = await service.get_user(user_id)
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user: {str(e)}")

@user_router.get("/users", response_model=List[User])
async def get_all_users(
    skip: int = 0, 
    limit: int = 100, 
    service: UserService = Depends(get_user_service)
):
    try:
        users = await service.get_all_users(skip, limit)
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")

@user_router.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: str, 
    update_data: UserUpdateRequest, 
    service: UserService = Depends(get_user_service)
):
    try:
        user = await service.update_user(user_id, update_data.model_dump(exclude_unset=True))
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

@user_router.delete("/users/{user_id}")
async def delete_user(user_id: str, service: UserService = Depends(get_user_service)):
    try:
        result = await service.delete_user(user_id)
        if result:
            return {"message": "User deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")