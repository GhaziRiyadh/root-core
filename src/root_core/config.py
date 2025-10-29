from datetime import datetime
from typing import List
from zoneinfo import ZoneInfo

from pydantic_settings import BaseSettings

from root_core.env_manager import EnvManager
from enum import Enum


class PermissionAction(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    FORCE_DELETE = "force_delete"
    RESTORE = "restore"
    LOGS = "logs"
    MANAGE = "manage"
    COPY = "copy"
    EXPORT = "export"


class Settings(BaseSettings):
    DATABASE_URI: str = EnvManager.get_env_variable(
        "DATABASE_URL", "sqlite:///database.db"
    )
    ASYCNC_DATABASE_URL: str = EnvManager.get_env_variable(
        "ASYNC_DATABASE_URL", "sqlite+aiosqlite:///database.db"
    )
    SECRET_KEY: str = EnvManager.get_env_variable("SECRET_KEY", "supersecretkey")
    ALGORITHM: str = EnvManager.get_env_variable("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        EnvManager.get_env_variable("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    PROJECT_NAME: str = EnvManager.get_env_variable(
        "PROJECT_NAME", "My FastAPI Project"
    )
    PROJECT_INFO: str = EnvManager.get_env_variable(
        "PROJECT_INFO", "My FastAPI Project"
    )
    PROJECT_VERSION: str = EnvManager.get_env_variable("PROJECT_VERSION", "1.0.0")
    TIME_ZONE: str = EnvManager.get_env_variable("TIME_ZONE", "Asia/Aden")
    UPLOAD_FOLDER: str = EnvManager.get_env_variable("UPLOAD_FOLDER", "uploads")
    STATIC_DIR: str = EnvManager.get_env_variable("STATIC_DIR", "static")

    # Base user model
    USER_MODEL: str = EnvManager.get_env_variable(
        "USER_MODEL", "root_core.apps.auth.models.user"
    )

    # Base log model
    LOG_MODEL: str = EnvManager.get_env_variable(
        "LOG_MODEL", "root_core.apps.base.models.log"
    )

    # actions

    ACTIONS: List[PermissionAction] = [action for action in PermissionAction]

    def get_now(self):
        """Get the current time in the configured time zone."""
        tz = ZoneInfo(self.TIME_ZONE)
        return datetime.now(tz)


settings = Settings()
