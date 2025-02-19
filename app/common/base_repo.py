# app/common/base_repo.py
from typing import TypeVar, Generic, List, Optional, Type, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import uuid
from core.db.database import MongoDBConnection

T = TypeVar('T', bound=BaseModel)

class BaseRepository(Generic[T]):
    def __init__(self, model_class: Type[T], collection_name: str, db: MongoDBConnection):
        self.model = model_class
        self.collection_name = collection_name
        self.db = db
        self.collection = db.get_collection(collection_name)

    async def create(self, item: T) -> T:
        """Create a new item in the database"""
        data = item.model_dump(by_alias=True)
        
        # Generate a new string ID if not present
        if "_id" not in data or not data["_id"]:
            data["_id"] = str(uuid.uuid4())
        
        # Add metadata fields
        data["created_at"] = datetime.utcnow()
        data["updated_at"] = datetime.utcnow()
        data["is_deleted"] = False

        await self.collection.insert_one(data)
        created_item = await self.collection.find_one({"_id": data["_id"]})
        return self.model.model_validate(created_item)

    async def get_by_id(self, id: str) -> Optional[T]:
        """Get an item by id"""
        item = await self.collection.find_one({"_id": id, "is_deleted": False})
        return self.model.model_validate(item) if item else None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all items with pagination"""
        cursor = self.collection.find({"is_deleted": False}).skip(skip).limit(limit)
        return [self.model.model_validate(doc) async for doc in cursor]

    async def update(self, id: str, data: Dict[str, Any]) -> Optional[T]:
        """Update an item partially"""
        data["updated_at"] = datetime.utcnow()
        
        result = await self.collection.update_one(
            {"_id": id, "is_deleted": False},
            {"$set": data}
        )

        if result.modified_count:
            updated_item = await self.collection.find_one({"_id": id})
            if updated_item:
                return self.model.model_validate(updated_item)
        return None

    async def delete(self, id: str) -> bool:
        """Soft delete an item"""
        result = await self.collection.update_one(
            {"_id": id, "is_deleted": False},
            {"$set": {"is_deleted": True, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0