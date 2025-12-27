import cmd
from datetime import datetime
import os
from re import L
from typing import List
from zoneinfo import ZoneInfo
from enum import Enum

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URI: str = Field(
        default="sqlite:///database.db", validation_alias="DATABASE_URL"
    )
    ASYNC_DATABASE_URI: str = Field(
        default="sqlite+aiosqlite:///database.db", validation_alias="ASYNC_DATABASE_URL"
    )
    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    PROJECT_NAME: str = "My FastAPI Project"
    PROJECT_INFO: str = "My FastAPI Project"
    PROJECT_VERSION: str = "1.0.0"
    TIME_ZONE: str = "Asia/Aden"
    UPLOAD_FOLDER: str = "uploads"
    STATIC_DIR: str = "static"

    # Base user model
    USER_MODEL: str = "core.apps.auth.models.user"

    # Base log model
    LOG_MODEL: str = "core.apps.base.models.log"

    # apps dir
    APPS_DIR: str = "core/apps"

    # Security Class
    SECURITY_CLASS: str = "core.bases.security.DefaultSecurity"

    # actions
    ACTIONS: List[PermissionAction] = [action for action in PermissionAction]

    CORE_APPS: str = "archive,base,auth"

    @property
    def core_apps(self) -> List[str]:
        return [app for app in self.CORE_APPS.split(",")]

    @property
    def app_dir(self) -> List[str]:
        """Get the applications directory."""
        return [
            os.path.join(*dir.strip().split("/")) for dir in self.APPS_DIR.split(",")
        ]

    @property
    def project_root(self) -> str:
        """Get the project root directory."""
        return os.getcwd()

    def get_now(self):
        """Get the current time in the configured time zone."""
        tz = ZoneInfo(self.TIME_ZONE)
        return datetime.now(tz)


settings = Settings()
