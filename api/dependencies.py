# api/dependencies.py
from app.user.user_repo import UserRepository
from app.user.user_service import UserService
from core.db.database import get_db_connection

def get_user_service():
    db = get_db_connection()
    repository = UserRepository(db)
    return UserService(repository)