import os
from pydantic_settings import BaseSettings
from typing import List


class Config(BaseSettings):
    ENV: str = "dev"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    LOG_HANDLERS: List[str] = ["console"]
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = int(os.getenv("PORT", 8000))

    # MongoDB Configuration
    MONGO_USERNAME: str = os.getenv("MONGO_INITDB_ROOT_USERNAME", "default_user")
    MONGO_PASSWORD: str = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "default_pass")
    MONGO_URI: str = os.getenv("MONGODB_LOCAL_URI", "mongodb://localhost:27017/mydatabase")

    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # JWT Configuration (Access Tokens)
    ACCESS_TOKEN_PRIVATE_KEY: str = os.getenv("ACCESS_TOKEN_PRIVATE_KEY", "")
    ACCESS_TOKEN_PUBLIC_KEY: str = os.getenv("ACCESS_TOKEN_PUBLIC_KEY", "")
    ACCESS_TOKEN_EXPIRED_IN: str = os.getenv("ACCESS_TOKEN_EXPIRED_IN", "15m")
    ACCESS_TOKEN_MAXAGE: int = int(os.getenv("ACCESS_TOKEN_MAXAGE", 15))

    # JWT Configuration (Refresh Tokens)
    REFRESH_TOKEN_PRIVATE_KEY: str = os.getenv("REFRESH_TOKEN_PRIVATE_KEY", "")
    REFRESH_TOKEN_PUBLIC_KEY: str = os.getenv("REFRESH_TOKEN_PUBLIC_KEY", "")
    REFRESH_TOKEN_EXPIRED_IN: str = os.getenv("REFRESH_TOKEN_EXPIRED_IN", "60m")
    REFRESH_TOKEN_MAXAGE: int = int(os.getenv("REFRESH_TOKEN_MAXAGE", 60))


class DevelopmentConfig(Config):
    ENV: str = "dev"
    LOG_LEVEL: str = "DEBUG"
    LOG_HANDLERS: List[str] = ["console"]


class ProductionConfig(Config):
    ENV: str = "prod"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    LOG_HANDLERS: List[str] = ["watchtower", "console"]


def get_config():
    env = os.getenv("ENV", "local")
    config_type = {
        "dev": DevelopmentConfig(),
        "prod": ProductionConfig(),
    }
    return config_type.get(env, Config())


config: Config = get_config()
