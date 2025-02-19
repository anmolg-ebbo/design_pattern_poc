from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, Any
from app.common.base_model import BaseDBModel

T = TypeVar('T', bound=BaseDBModel)

class IBaseRepository(ABC, Generic[T]):
    @abstractmethod
    async def create(self, data: T) -> T:
        pass

    @abstractmethod
    async def get_by_id(self, id: str) -> Optional[T]:
        pass

    @abstractmethod
    async def update(self, id: str, data: Dict[str, Any]) -> Optional[T]:
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        pass