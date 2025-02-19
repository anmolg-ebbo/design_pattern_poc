import os
from typing import List

from fastapi import FastAPI, Depends, Request
from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.health import health_router
from core.dependencies.logging import Logging
from core.exceptions.base import CustomException
from api.user import user_router


def init_routes(app: FastAPI) -> None:
    """
    method takes the fastApi app as argument
    New Routes should be added here
    """
    
    app.include_router(health_router, tags=["health"])
    app.include_router(user_router, tags=["user"])
    return




def init_middleware() -> List[Middleware]:
    """
    Initialize  middleware classes
    """
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
    
        # Middleware(LogEntryMiddleware),
    ]
    return middleware


def init_dependencies() -> List[Depends]:
    """initialize dependencies like logging"""
    dependencies = []
    # Logging()
    return dependencies


def init_listeners(app: FastAPI) -> None:
    # Exception handler
    _logger = Logging.get_logger(__name__)



def create_app() -> FastAPI:
    """Creates an instance of FastApi App"""
    app = FastAPI(
        title="catalyst",
        docs_url="/docs",
        middleware=init_middleware(),
        dependencies=init_dependencies(),
    )
    init_routes(app=app)
    init_listeners(app=app)
    return app


app = create_app()