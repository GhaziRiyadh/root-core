from datetime import datetime
from typing import List
from zoneinfo import ZoneInfo

from pydantic_settings import BaseSettings

from core.env_manager import EnvManager
from enum import Enum


class PermissionAction(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    FORCE_DELETE = "force_delete"
    RESTORE = "restore"
    LOGS = "logs"
    MANAGE = "management"
    COPY = "copy"
    EXPORT = "export"


class Settings(BaseSettings):
    DATABASE_URI: str = EnvManager.get("DATABASE_URL", "sqlite:///database.db")
    ASYNC_DATABASE_URI: str = EnvManager.get(
        "ASYNC_DATABASE_URL", "sqlite+aiosqlite:///database.db"
    )
    SECRET_KEY: str = EnvManager.get("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = EnvManager.get("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        EnvManager.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    PROJECT_NAME: str = EnvManager.get("PROJECT_NAME", "My FastAPI Project")
    PROJECT_INFO: str = EnvManager.get("PROJECT_INFO", "My FastAPI Project")
    PROJECT_VERSION: str = EnvManager.get("PROJECT_VERSION", "1.0.0")
    TIME_ZONE: str = EnvManager.get("TIME_ZONE", "Asia/Aden")
    UPLOAD_FOLDER: str = EnvManager.get("UPLOAD_FOLDER", "uploads")
    STATIC_DIR: str = EnvManager.get("STATIC_DIR", "static")

    # Base user model
    USER_MODEL: str = EnvManager.get("USER_MODEL", "core.apps.auth.models.user")

    # Base log model
    LOG_MODEL: str = EnvManager.get("LOG_MODEL", "core.apps.base.models.log")

    # apps dir
    APPS_DIR: str = EnvManager.get("APPS_DIR", "apps")

    # Kafka configuration
    KAFKA_BOOTSTRAP_SERVERS: str = EnvManager.get(
        "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
    )
    KAFKA_CONSUMER_GROUP: str = EnvManager.get(
        "KAFKA_CONSUMER_GROUP", f"{PROJECT_NAME}-consumer-group"
    )
    KAFKA_AUTO_OFFSET_RESET: str = EnvManager.get(
        "KAFKA_AUTO_OFFSET_RESET", "earliest"
    )

    GET_USER_FUNCTION: str | None = EnvManager.get(
        "GET_USER_FUNCTION",None
    )

    # actions

    ACTIONS: List[PermissionAction] = [action for action in PermissionAction]

    def get_now(self):
        """Get the current time in the configured time zone."""
        tz = ZoneInfo(self.TIME_ZONE)
        return datetime.now(tz)


settings = Settings()
