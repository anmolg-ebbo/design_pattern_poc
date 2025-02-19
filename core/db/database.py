# core/db/database.py
import os
from motor.motor_asyncio import AsyncIOMotorClient

class MongoDBConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        # Configuration
        self.uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = os.getenv("DB_NAME", "design_pattern_poc")
        
        # Create MongoDB client (async motor client)
        self.client = AsyncIOMotorClient(self.uri)
        self.db = self.client[self.db_name]
    
    def get_collection(self, collection_name: str):
        return self.db[collection_name]
    
    async def close(self):
        self.client.close()

# Singleton instance
def get_db_connection() -> MongoDBConnection:
    return MongoDBConnection()