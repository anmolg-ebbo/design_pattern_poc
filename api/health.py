from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import JSONResponse
from core.db.database import MongoDBConnection
from pydantic import BaseModel
health_router = APIRouter()


@health_router.get("/health")
async def health():
    """
    API  health check endpoint
    """
    return {"status": "OK"}

@health_router.get("/health/database")
async def check_database_health():
    try:
        db = MongoDBConnection()

        # Define a simple model for health check
        class HealthCheckModel(BaseModel):
            status: str

        async with db.get_collection_with_encryption("health_check", HealthCheckModel) as collection:
            database = collection.database  
            await database.command("ping")  
        
        return {"status": "ok", "message": "Database connection successful"}

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": f"Database connection failed: {str(e)}"}
        )
